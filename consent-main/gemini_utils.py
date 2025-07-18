import google.generativeai as genai
import streamlit as st
from config import HARDCODED_BASE_EXPLANATIONS # REVERSE_SECTIONS_MAP 임포트 제거

_model = None

def configure_gemini(api_key):
    try:
        genai.configure(api_key=api_key)
        global _model
        _model = genai.GenerativeModel('gemini-2.0-flash')
        return True
    except Exception as e:
        st.error(f"Gemini API 키 설정 또는 모델 초기화에 실패했습니다: {e}")
        return False

def get_gemini_chat_response(chat_history_list, current_user_message, initial_explanation=""):
    if _model is None:
        st.error("Gemini 모델이 설정되지 않았습니다. configure_gemini를 먼저 호출하세요.")
        return "AI 모델을 사용할 수 없습니다. 관리자에게 문의해주세요."

    gemini_history = []
    
    if initial_explanation and not any(msg.get('role') == 'assistant' and initial_explanation in msg.get('content', '') for msg in chat_history_list):
        gemini_history.append({"role": "model", "parts": [{"text": initial_explanation}]})
    
    for msg in chat_history_list:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [{"text": msg["content"]}]})
    
    try:
        chat = _model.start_chat(history=gemini_history)
        
        response = chat.send_message(current_user_message)
        
        return response.text
    except Exception as e:
        st.error(f"Gemini API 호출 중 오류 발생: {e}")
        return "죄송합니다. AI 모델이 응답하는 데 문제가 발생했습니다. 잠시 후 다시 시도해주세요."


def get_gemini_response_from_combined_content(user_profile=None, current_section_title="현재 섹션"):
    if _model is None:
        st.error("Gemini 모델이 설정되지 않았습니다. configure_gemini를 먼저 호출하세요.")
        return "AI 모델을 사용할 수 없습니다. 관리자에게 문의해주세요."

    age = user_profile.get('age', '알 수 없음')
    diagnosis = user_profile.get('diagnosis', '알 수 없음')
    surgery = user_profile.get('surgery', '알 수 없음')
    history_display = user_profile.get('history', '없음')
    allergy = user_profile.get('allergy', '없음')

    # 한국어 섹션 제목을 직접 키로 사용
    hardcoded_base_explanation = HARDCODED_BASE_EXPLANATIONS.get(current_section_title, {}).get(diagnosis)
    
    if not hardcoded_base_explanation:
        return f"죄송합니다. '{current_section_title}' 섹션의 '{diagnosis}'에 대한 하드코딩된 설명 내용을 찾을 수 없습니다. 관리자에게 문의해주세요."

    history_context = ""
    if history_display and history_display != '없음':
        if "고혈압" in history_display:
            history_context += "환자분께 고혈압이 있으시다면 수술 전 혈압 조절의 중요성을 언급해주세요. "
        if "당뇨" in history_display:
            history_context += "당뇨가 있으시다면 수술 중후 혈당 관리의 중요성을 언급해주세요. "
        if "과거수술력" in history_display:
            history_context += "과거 수술 이력을 고려하여 유착 등 가능성을 언급하고, 의료진이 준비하고 있음을 안심시켜주세요. "
        if not history_context:
            history_context += f"가지고 계신 과거력({history_display})에 대해 의료진이 잘 알고 대비하고 있음을 안심시켜주세요. "
    
    allergy_context = ""
    if allergy and allergy != '없음':
        allergy_context = f"특이체질이나 알레르기({allergy})가 수술 중 발생할 수 있는 상황에 어떤 영향을 줄 수 있는지, 의료진이 미리 알고 주의를 기울일 것임을 알려주세요. "
    
    age_context = ""
    if age != '알 수 없음':
        if age < 18:
            age_context = f"{age}세의 어린 환자분에게는 특별히 더 섬세한 접근이 필요하고, 의료진이 최선을 다할 것임을 강조해주세요. "
        elif age >= 60:
            age_context = f"{age}세이시므로, 연세가 있으신 만큼 수술 전 검사와 회복 과정 관리에 더 신경 쓸 것임을 언급해주세요. "
    
    positive_outcome_context = ""
    if surgery and surgery != '알 수 없음' and surgery != '기타':
        positive_outcome_context = f"이번 {surgery}를 통해 환자분께 기대되는 긍정적인 효과와 개선점을 명확히 설명하고 희망적인 메시지를 주세요. "
    
    full_prompt = f"""
    당신은 수술 전 동의서를 설명해주는 의료 커뮤니케이션 전문가입니다.
    {diagnosis} 환자분께 {current_section_title}에 대해 설명해 주세요.

    **환자 맞춤형 설명 지침 (설명에 자연스럽게 녹여주세요):**
    - 환자의 연령({age}세)에 따라 수술 중 발생할 수 있는 상황에 어떤 영향을 줄 수 있는지 설명해주세요.
        - {age_context}
    - 환자의 과거력({history_display})이나 기저질환이 수술 과정이나 회복에 어떤 영향을 줄 수 있는지 구체적으로 설명해 주세요.
        - {history_context}
    - 특이체질({allergy})이나 복용 중인 약물이 수술 중 발생할 수 있는 상황에 어떤 영향을 줄 수 있는지 알려 주세요.
        - {allergy_context}
    - 수술명({surgery})과 연결하여 수술이 환자에게 가져올 긍정적인 효과와 개선 기대를 설명하고 희망적인 메시지를 주세요.
        - {positive_outcome_context}
    
    ---
    **[기본 설명]:**
    {hardcoded_base_explanation}

    위 [기본 설명]을 바탕으로 환자분의 프로필 정보를 추가하여 개인화하고, 더 자세히 설명해 주세요.
    내용은 500자 내외로 전해 주세요.
    ---
    """
    
    try:
        response = _model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Gemini API 호출 중 오류 발생: {e}")
        return "죄송합니다. AI 모델이 응답하는 데 문제가 발생했습니다. 잠시 후 다시 시도해주세요."