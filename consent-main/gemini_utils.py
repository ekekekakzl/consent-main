import google.generativeai as genai
import streamlit as st
from config import HARDCODED_BASE_EXPLANATIONS, SECTIONS_ORDER_KEYS # SECTIONS_ORDER_KEYS 임포트 추가

_model = None

def configure_gemini(api_key):
    """
    Gemini API 키를 설정하고 모델을 초기화합니다.
    이 함수는 앱 시작 시 한 번만 호출되어야 합니다.
    """
    try:
        genai.configure(api_key=api_key)
        global _model
        _model = genai.GenerativeModel('gemini-2.0-flash')
        return True
    except Exception as e:
        st.error(f"Gemini API 키 설정 또는 모델 초기화에 실패했습니다: {e}")
        return False

def get_gemini_chat_response(chat_history_list, current_user_message, initial_explanation="", user_profile=None):
    """
    채팅 기록과 현재 사용자 메시지를 Gemini에 전송하여 응답을 받습니다.
    Args:
        chat_history_list (list): 이전 대화의 메시지 목록 (role, content 포함).
                                 여기서는 Streamlit의 st.session_state.chat_history 형식을 따릅니다.
        current_user_message (str): 현재 사용자 메시지.
        initial_explanation (str): 현재 섹션의 초기 설명 (Gemini에게 컨텍스트로 제공).
        user_profile (dict, optional): 환자의 프로필 정보. 기본값은 None.
    Returns:
        str: Gemini의 응답 텍스트.
    """
    if _model is None:
        st.error("Gemini 모델이 설정되지 않았습니다. configure_gemini를 먼저 호출하세요.")
        return "AI 모델을 사용할 수 없습니다. 관리자에게 문의해주세요."

    # 초기 시스템 메시지 구성
    system_instruction = "당신은 로봇수술 동의서 설명을 돕는 친절하고 전문적인 AI 어시스턴트입니다. 환자의 질문에 대해 쉽고 명확하게 답변해주세요."
    if user_profile:
        patient_name = user_profile.get('name', '환자분')
        patient_age = user_profile.get('age', '알 수 없음')
        patient_gender = user_profile.get('gender', '알 수 없음')
        patient_diagnosis = user_profile.get('diagnosis', '알 수 없음')
        patient_education = user_profile.get('education_level', '알 수 없음')

        system_instruction += (
            f" 현재 대화 중인 환자분은 '{patient_name}'님이며, {patient_age}세 {patient_gender}이십니다. "
            f"진단명은 '{patient_diagnosis}'이며, 이해 수준은 '{patient_education}'입니다. "
            f"이 정보를 바탕으로 환자분의 눈높이에 맞춰 답변해주세요. 특히 진단명과 관련된 질문에는 해당 병명을 언급하며 구체적으로 설명해주세요."
        )

    # Gemini API의 대화 기록 형식에 맞게 변환
    gemini_history = []
    
    # 시스템 지시를 첫 번째 메시지로 추가
    gemini_history.append({"role": "user", "parts": [{"text": system_instruction}]})

    # 이전 대화 기록 추가
    # initial_explanation이 있고, 이미 기록에 포함되지 않았다면 model의 첫 메시지로 추가
    if initial_explanation and not any(msg.get('role') == 'assistant' and initial_explanation in msg.get('content', '') for msg in chat_history_list):
        gemini_history.append({"role": "model", "parts": [{"text": initial_explanation}]})
    
    for msg in chat_history_list:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [{"text": msg["content"]}]})
    
    try:
        # start_chat에 history를 직접 전달하여 대화 컨텍스트 유지
        chat = _model.start_chat(history=gemini_history)
        
        response = chat.send_message(current_user_message)
        
        return response.text
    except Exception as e:
        st.error(f"Gemini API 호출 중 오류 발생: {e}")
        return "죄송합니다. AI 모델이 응답하는 데 문제가 발생했습니다. 잠시 후 다시 시도해주세요."


def get_gemini_response_from_combined_content(user_profile=None, current_section_title="현재 섹션"):
    """
    하드코딩된 기본 설명을 바탕으로 Gemini AI로부터 개인화된 설명을 생성합니다.
    하드코딩된 설명이 없을 경우, 설명이 없음을 알립니다.
    또한, 공통 설명이 있는 경우 이를 참조하여 가져옵니다.
    """
    if _model is None:
        st.error("Gemini 모델이 설정되지 않았습니다. configure_gemini를 먼저 호출하세요.")
        return "AI 모델을 사용할 수 없습니다. 관리자에게 문의해주세요."

    age = user_profile.get('age', '알 수 없음')
    diagnosis = user_profile.get('diagnosis', '알 수 없음')
    surgery = user_profile.get('surgery', '알 수 없음')
    history_display = user_profile.get('history', '없음')

    # HARDCODED_BASE_EXPLANATIONS에서 해당 섹션의 설명을 가져옵니다.
    section_explanations = HARDCODED_BASE_EXPLANATIONS.get(current_section_title, {})
    
    # 진단명에 해당하는 설명 항목을 가져옵니다.
    diagnosis_specific_entry = section_explanations.get(diagnosis)
    
    final_explanation_content = ""

    if isinstance(diagnosis_specific_entry, dict):
        # 진단명 항목이 딕셔너리인 경우 (예: "수술 방법" 섹션)
        base_key_or_content = diagnosis_specific_entry.get("base_explanation")
        additional_content = diagnosis_specific_entry.get("additional_explanation", "")
        
        common_content = ""
        if base_key_or_content == "_common_explanation":
            common_content = section_explanations.get("_common_explanation", "")
        elif isinstance(base_key_or_content, str): # base_explanation 자체가 내용일 경우
            common_content = base_key_or_content

        final_explanation_content = common_content
        if additional_content: # 추가 설명이 있는 경우에만 붙입니다.
            final_explanation_content += "\n\n" + additional_content
            
    elif isinstance(diagnosis_specific_entry, str):
        # 진단명 항목이 문자열인 경우 (예: "수술 필요성" 섹션)
        if diagnosis_specific_entry == "_common_explanation":
            final_explanation_content = section_explanations.get("_common_explanation", "")
        else:
            final_explanation_content = diagnosis_specific_entry # 직접 설명 텍스트인 경우
    
    if not final_explanation_content.strip():
        return f"죄송합니다. '{current_section_title}' 섹션의 '{diagnosis}'에 대한 설명 내용을 찾을 수 없습니다. 관리자에게 문의해주세요."

    hardcoded_base_explanation = final_explanation_content

    history_context = ""
    if history_display and history_display != '없음':
        if "고혈압" in history_display:
            history_context += "환자분께 고혈압이 있으시다면 수술 전 혈압 조절의 중요성을 언급해주세요. "
        if "당뇨" in history_display:
            history_context += "당뇨가 있으시다면 수술 중후 혈당 관리의 중요성을 언급해주세요. "
        if "과거력" in history_display:
            history_context += "과거 수술 이력을 고려하여 유착 등 가능성을 언급하고, 의료진이 준비하고 있음을 안심시켜주세요. "
        if not history_context:
            history_context += f"가지고 계신 과거력이나 기존 질환, 알레르기({history_display})에 대해 의료진이 잘 알고 대비하고 있음을 안심시켜주세요. "

    
    age_context = ""
    if age != '알 수 없음':
        if age < 18:
            age_context = f"{age}세의 어린 환자분에게는 특별히 더 섬세한 접근이 필요하고, 의료진이 최선을 다할 것임을 강조해주세요. "
        elif age >= 70:
            age_context = f"{age}세이시므로, 연세가 있으신 만큼 수술 전 검사와 회복 과정 관리에 더 신경 쓸 것임을 언급해주세요. "
    
    full_prompt = f"""
    당신은 수술 전 동의서를 설명해주는 의료 커뮤니케이션 전문가입니다.
    아래 제공된 [로봇수술동의서 내용]을 바탕으로 {diagnosis} 환자분께 {current_section_title}에 대해 설명해 주세요.

    **설명 지침:**
    - 환자분이 이해할 수 있도록 설명해 주세요.
    - 불안해하는 환자에게 따뜻하고 안심되는 말투로 설명해 주세요. 공감과 신뢰를 주는 문장을 넣어 주세요.
    - 필요한 경우 간단한 예시나 비유를 사용해 주세요.
    - 설명 마지막에는 긍정적인 마무리 표현을 추가해 주세요.
    - 설명이 끝난 후, 환자분에게 "혹시 제가 설명드린 부분 중에 궁금한 점이나 더 알고 싶은 부분이 있으실까요?" 와 같은 질문을 넣어 이해도를 확인하거나 생각을 유도해 주세요.

    ---
    **[로봇수술동의서 내용]:**
    {hardcoded_base_explanation}
    ---
    **[AI 어시스턴트의 따뜻하고 정확한 설명]:**
    """
    
    try:
        response = _model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Gemini API 호출 중 오류 발생: {e}")
        return "죄송합니다. AI 모델이 응답하는 데 문제가 발생했습니다. 잠시 후 다시 시도해주세요."


def get_overall_consent_summary(user_profile):
    """
    환자 프로필을 바탕으로 로봇수술 동의서 전체 내용을 요약하여 생성합니다.
    """
    if _model is None:
        st.error("Gemini 모델이 설정되지 않았습니다. configure_gemini를 먼저 호출하세요.")
        return "AI 모델을 사용할 수 없습니다. 관리자에게 문의해주세요."

    patient_name = user_profile.get('name', '환자분')
    patient_age = user_profile.get('age', '알 수 없음')
    patient_gender = user_profile.get('gender', '알 수 없음')
    patient_diagnosis = user_profile.get('diagnosis', '알 수 없음')
    patient_surgery = user_profile.get('surgery', '알 수 없음')
    patient_education = user_profile.get('education_level', '알 수 없음')

    # 모든 섹션 제목을 포함하여 프롬프트 구성
    all_sections_titles = ", ".join([
        "수술 필요성", "수술 방법", "고려 사항", "부작용", "주의사항", "자기 결정권"
    ])

    summary_prompt = f"""
    당신은 로봇수술 동의서 설명을 돕는 의료 커뮤니케이션 전문가입니다.
    '{patient_name}'님({patient_age}세 {patient_gender}, 진단명: {patient_diagnosis}, 수술명: {patient_surgery}, 이해 수준: {patient_education})께 로봇수술 동의서의 전체 내용을 요약하여 설명해주세요.
    환자분께서는 이미 다음 섹션들에 대한 설명을 들었습니다: {all_sections_titles}.

    **요약 지침:**
    - 모든 섹션의 핵심 내용을 통합하여 간결하고 명확하게 요약해 주세요.
    - 환자분이 이해하기 쉽도록 친절하고 따뜻한 말투를 사용해 주세요.
    - 환자분의 진단명('{patient_diagnosis}')과 수술명('{patient_surgery}')을 명확히 언급하며, 이 수술이 환자분께 왜 중요하고 어떤 과정을 거치며, 어떤 점을 주의해야 하는지 등을 포함해 주세요.
    - 긍정적이고 안심시키는 어조로 마무리해 주세요.
    - 요약은 약 200-300단어 내외로 작성해 주세요.

    **[로봇수술 동의서 전체 요약]:**
    """

    try:
        response = _model.generate_content(summary_prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Gemini API 호출 중 오류 발생: {e}")
        return "죄송합니다. AI 모델이 전체 요약을 생성하는 데 문제가 발생했습니다. 잠시 후 다시 시도해주세요."