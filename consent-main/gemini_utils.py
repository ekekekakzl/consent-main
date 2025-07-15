import google.generativeai as genai
import streamlit as st

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


def get_gemini_response_from_combined_content(combined_content, user_profile=None, current_section_title="현재 섹션"):
    if _model is None:
        st.error("Gemini 모델이 설정되지 않았습니다. configure_gemini를 먼저 호출하세요.")
        return "AI 모델을 사용할 수 없습니다. 관리자에게 문의해주세요."

    age = user_profile.get('age', '알 수 없음')
    diagnosis = user_profile.get('diagnosis', '알 수 없음')
    surgery = user_profile.get('surgery', '알 수 없음')
    history_display = user_profile.get('history', '없음')
    allergy = user_profile.get('allergy', '없음')

    history_context = ""
    # 과거력이 '없음'이거나 비어있지 않을 경우에만 컨텍스트를 생성
    if history_display and history_display != '없음':
        if "고혈압" in history_display:
            history_context += "환자분께 고혈압이 있으시다면 수술 전 혈압 조절의 중요성을 언급해주세요. "
        if "당뇨" in history_display:
            history_context += "당뇨가 있으시다면 수술 중후 혈당 관리의 중요성을 언급해주세요. "
        if "과거수술력" in history_display:
            history_context += "과거 수술 이력을 고려하여 유착 등 가능성을 언급하고, 의료진이 준비하고 있음을 안심시켜주세요. "
        # 특정 키워드 외의 과거력이 있을 경우 일반적인 안심 문구 추가
        if not history_context:
            history_context += f"가지고 계신 과거력({history_display})에 대해 의료진이 잘 알고 대비하고 있음을 안심시켜주세요. "
    
    allergy_context = ""
    # 특이체질/알레르기가 '없음'이거나 비어있지 않을 경우에만 컨텍스트를 생성
    if allergy and allergy != '없음':
        allergy_context = f"특이체질이나 알레르기({allergy})가 수술 중 발생할 수 있는 상황에 어떤 영향을 줄 수 있는지, 의료진이 미리 알고 주의를 기울일 것임을 알려주세요. "
    
    age_context = ""
    if age != '알 수 없음':
        if age < 18:
            age_context = f"{age}세의 어린 환자분에게는 특별히 더 섬세한 접근이 필요하고, 의료진이 최선을 다할 것임을 강조해주세요. "
        elif age >= 70:
            age_context = f"{age}세이시므로, 연세가 있으신 만큼 수술 전 검사와 회복 과정 관리에 더 신경 쓸 것임을 언급해주세요. "
    
    positive_outcome_context = ""
    if surgery and surgery != '알 수 없음' and surgery != '기타':
        positive_outcome_context = f"이번 {surgery}를 통해 환자분께 기대되는 긍정적인 효과와 개선점을 명확히 설명하고 희망적인 메시지를 주세요. "
    
    full_prompt = f"""
    당신은 수술 전 동의서를 설명해주는 의료 커뮤니케이션 전문가입니다.
    아래 제공된 [로봇수술동의서 내용]을 바탕으로 {diagnosis} 환자분께 {current_section_title}에 대해 이해하기 쉽게 설명해 주세요요.

    **설명 지침:**
    - 환자분이 이해할 수 있도록 설명하는 어투로 말해주세요요.
    - 불안해하는 환자에게 따뜻하고 안심되는 말투로 설명해 주세요. 공감하는 말 한두 문장을 꼭 넣어 주세요.
    - 의학적인 의미는 그대로 유지해 주세요.
    - 의학 용어는 초등학생이 이해하기 쉬운 말로 풀어서 바꿔 주세요.
    - 글의 난이도는 초등학생이 이해할 수 있는 수준으로 작성해주세요.
    - 문장은 짧고 명확하게 써 주세요. 불필요한 수식어나 복잡한 문장은 피하고, 핵심 내용만 전달할 수 있도록 짧고 명확하게 써주세요.
    - 필요한 경우 간단한 예시나 비유를 사용해 주세요.
    - 내용은 500자 내외로 전해 주세요.
    - 위험이나 부작용은 있는 그대로 설명하되, 너무 자극적인 표현은 피하고 부드럽고 신뢰를 주는 말로 바꿔 주세요. 설명 마지막에는 긍정적인 마무리 표현을 꼭 추가해 주세요.

    **환자 맞춤형 설명 지침 (설명에 자연스럽게 녹여주세요):**
    - 환자의 연령({age}세)에 따라 수술 중 발생할 수 있는 상황에 어떤 영향을 줄 수 있는지 설명해주세요.
        - {age_context}
    - 환자의 과거력({history_display})이나 기저질환이 수술 과정이나 회복에 어떤 영향을 줄 수 있는지 구체적으로 설명해 주세요.
        - {history_context}
    - 특이체질({allergy})이나 복용 중인 약물이 수술 중 발생할 수 있는 상황에 어떤 영향을 줄 수 있는지 알려 주세요.
        - {allergy_context}
    - 수술명({surgery})과 연결하여 수술이 환자에게 가져올 긍정적인 효과와 개선 기대를 명확히 설명하고 희망적인 메시지를 주세요.
        - {positive_outcome_context}
    
    **마무리:**
    - 설명이 끝난 후, 환자분에게 **"혹시 제가 설명드린 부분 중에 궁금한 점이나 더 알고 싶은 부분이 있으실까요?"** 와 같은 질문을 넣어 이해도를 확인해주세요.
    - 밑에 문제를 풀면서 한번 더 확인하는 시간을 가져보도록 유도해주세요.

    ---
    **[로봇수술동의서 내용]:**
    {combined_content}
    ---

    **[AI 어시스턴트의 따뜻하고 맞춤형 설명]:**
    """
    
    try:
        response = _model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Gemini API 호출 중 오류 발생: {e}")
        return "죄송합니다. AI 모델이 응답하는 데 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
