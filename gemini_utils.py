import google.generativeai as genai
import streamlit as st
from gtts import gTTS
import io

def configure_gemini(user_profile):
    """
    환자 프로필을 기반으로 Gemini 모델을 설정하고 초기화합니다.
    """
    try:
        if not user_profile:
            st.error("모델 설정에 필요한 사용자 정보가 없습니다.")
            return None

        patient_gender = user_profile.get('gender', '알 수 없음')
        patient_surgery = user_profile.get('surgery', '알 수 없음')
        
        patient_info = (
            f"현재 상담 중인 환자분은 {patient_gender}이며, '{patient_surgery}' 수술을 앞두고 있습니다. "
            "이 정보를 바탕으로 환자분의 상황에 맞게 답변해주세요."
        )
        
        system_instruction = (
            "당신은 로봇수술 동의서 설명을 돕는 친절하고 전문적인 의료진입니다. "
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
    surgery_specific_entry = section_explanations.get(surgery)
    final_explanation_content = ""

    if isinstance(surgery_specific_entry, dict):
        base_key = surgery_specific_entry.get("base_explanation")
        additional_content = surgery_specific_entry.get("additional_explanation", "")
        common_content = section_explanations.get(base_key, "") if base_key == "_common_explanation" else base_key
        final_explanation_content = (common_content or "") + "\n\n" + (additional_content or "")
    elif isinstance(surgery_specific_entry, str):
        final_explanation_content = section_explanations.get(surgery_specific_entry, surgery_specific_entry)

    if not final_explanation_content.strip():
        return f"죄송합니다. '{current_section_title}' 섹션의 '{surgery}'에 대한 설명 내용을 찾을 수 없습니다."

    return final_explanation_content.strip()

def get_overall_consent_summary(model):
    """
    환자 프로필을 바탕으로 동의서 전체 내용을 요약하여 생성합니다.
    """
    if model is None:
        return "요약 기능을 사용할 수 없습니다. 모델이 초기화되지 않았습니다."

    user_profile = st.session_state.user_profile
    summary_prompt = "앞서 설명한 동의서의 전체 핵심 내용을 환자분이 이해하기 쉽게 요약해주세요."

    try:
        response = model.generate_content(summary_prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"요약 생성 중 오류 발생: {e}")
        return "죄송합니다. 전체 요약을 생성하는 데 문제가 발생했습니다."

@st.cache_data(show_spinner=False)
def synthesize_speech(text: str) -> bytes:
    """
    gTTS를 사용하여 텍스트를 음성으로 변환하고 MP3 바이트를 반환합니다.
    """
    try:
        tts = gTTS(text=text, lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        st.error(f"음성 합성 중 오류 발생: {e}")
        return b""