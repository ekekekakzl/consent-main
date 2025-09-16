import google.generativeai as genai
import streamlit as st

def configure_gemini(user_profile):
    """
    환자 프로필을 기반으로 Gemini 모델을 설정하고 초기화합니다.
    """
    try:
        if not user_profile:
            st.error("모델 설정에 필요한 사용자 정보가 없습니다.")
            return None

        patient_surgery = user_profile.get('surgery', '알 수 없음')
        
        system_instruction = (
            "당신은 로봇수술 동의서 설명을 돕는 친절하고 전문적인 의료진입니다. "
            f"현재 상담 중인 환자분은 '{patient_surgery}' 수술을 앞두고 있습니다. "
            "환자의 질문에 대해 의학적 사실에 기반하여 쉽고 명확하게 답변해주세요. "
            "따뜻하고 공감하는 어조를 유지하며, 환자를 안심시켜주세요. "
        )
        
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash-latest',
            system_instruction=system_instruction
        )
        return model
    except Exception as e:
        st.error(f"응답 모델을 설정하는 데 실패했습니다: {e}")
        return None

def get_gemini_response_from_combined_content(user_profile, current_section_title):
    """
    config.py에서 하드코딩된 기본 설명을 수술명에 따라 가져옵니다.
    """
    from config import HARDCODED_BASE_EXPLANATIONS

    surgery = user_profile.get('surgery', '알 수 없음')
    section_explanations = HARDCODED_BASE_EXPLANATIONS.get(current_section_title, {})
    
    explanation_content = section_explanations.get(surgery, "")

    if isinstance(explanation_content, dict):
        base = section_explanations.get(explanation_content.get("base_explanation"), "")
        additional = explanation_content.get("additional_explanation", "")
        return f"{base}\n\n{additional}"
    elif explanation_content == "_common_explanation":
        return section_explanations.get("_common_explanation", "")
    
    return explanation_content or f"'{surgery}'에 대한 '{current_section_title}' 설명이 준비되지 않았습니다."

def get_overall_consent_summary(model):
    """
    환자 프로필을 바탕으로 동의서 전체 내용을 요약하여 생성합니다.
    """
    if model is None:
        return "요약 기능을 사용할 수 없습니다. 모델이 초기화되지 않았습니다."

    summary_prompt = "앞서 설명한 동의서의 전체 핵심 내용을 환자분이 이해하기 쉽게 요약해주세요."

    try:
        response = model.generate_content(summary_prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"요약 생성 중 오류 발생: {e}")
        return "죄송합니다. 전체 요약을 생성하는 데 문제가 발생했습니다."