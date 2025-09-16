import streamlit as st
import base64
import re
from gemini_utils import get_overall_consent_summary, synthesize_speech

def _play_text_as_audio_callback(text_to_speak):
    """
    텍스트를 음성으로 변환하여 재생하는 콜백 함수.
    """
    cleaned_text = re.sub(r'[^\w\s.,?!가-힣a-zA-Z0-9]', ' ', text_to_speak)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    audio_bytes = synthesize_speech(cleaned_text)
    if audio_bytes:
        base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
        audio_html = f"""
        <audio controls autoplay style="width: 100%; margin-top: 10px;">
            <source src="data:audio/mp3;base64,{base64_audio}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        st.session_state.current_audio_html = audio_html
    else:
        st.error("음성 생성에 실패했습니다. 인터넷 연결을 확인하거나 잠시 후 다시 시도해주세요.")
        st.session_state.current_audio_html = ""

def render_final_summary_page():
    """
    전체 내용을 요약하여 표시하는 페이지를 렌더링합니다.
    """
    st.markdown("<h1 class='summary-title'>전체 동의서 요약 📝</h1>", unsafe_allow_html=True)
    st.info("지금까지 설명드린 전체 주요 내용을 요약해 드립니다.")

    # 세션에 요약 내용이 없으면 AI를 통해 새로 생성합니다.
    if not st.session_state.get('overall_summary_content'):
        with st.spinner("요약 내용을 생성 중입니다..."):
            # app.py에서 생성된 모델 객체를 사용합니다.
            summary_text = get_overall_consent_summary(st.session_state.model)
            st.session_state.overall_summary_content = summary_text
    
    st.markdown("---")

    # 생성된 요약 내용을 화면에 표시합니다.
    if st.session_state.overall_summary_content:
        st.markdown(st.session_state.overall_summary_content)
        st.button("음성 재생 ▶️", key="play_summary_content", use_container_width=True,
                  on_click=_play_text_as_audio_callback, args=(st.session_state.overall_summary_content,))
    else:
        st.warning("요약 내용을 불러오는 데 실패했습니다.")

    st.markdown("---")
    col_back_to_main, col_re_enter_profile = st.columns(2)
    with col_back_to_main:
        if st.button("이전단계", key="back_to_main_from_summary", use_container_width=True):
            st.session_state.current_page = "final_chat" # 최종 채팅 페이지로 돌아갑니다.
            st.session_state.overall_summary_content = "" # 요약 내용 초기화
            st.session_state.current_audio_html = ""
            st.rerun()
            
    with col_re_enter_profile:
        if st.button("정보 다시 입력하기", key="re_enter_profile_from_summary", use_container_width=True):
            # 모든 세션 상태를 초기화하여 처음부터 다시 시작합니다.
            st.session_state.profile_setup_completed = False
            st.session_state.current_page = "profile_setup"
            st.session_state.user_profile = {}
            st.session_state.chat_history = []
            st.session_state.quiz_answers = {}
            st.session_state.current_section = 0
            st.session_state.current_gemini_explanation = ""
            st.session_state.last_loaded_section_key = None
            st.session_state.show_quiz = False
            st.session_state.current_quiz_idx = 0
            st.session_state.current_faq_answer = ""
            st.session_state.overall_summary_content = ""
            st.session_state.current_audio_html = ""
            st.rerun()
