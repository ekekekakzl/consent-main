import streamlit as st
from gemini_utils import get_overall_consent_summary
# 새로 만든 오디오 유틸리티 파일에서 콜백 함수를 가져옵니다.
from ui_modules.audio_utils import play_text_as_audio_callback

def render_final_summary_page():
    """
    전체 내용을 요약하여 표시하는 페이지를 렌더링합니다.
    """
    st.markdown("<h1 class='summary-title'>전체 동의서 요약 📝</h1>", unsafe_allow_html=True)
    st.info("지금까지 설명드린 전체 주요 내용을 요약해 드립니다.")

    if not st.session_state.get('overall_summary_content'):
        with st.spinner("요약 내용을 생성 중입니다..."):
            summary_text = get_overall_consent_summary(st.session_state.model)
            st.session_state.overall_summary_content = summary_text
    
    st.markdown("---")

    if st.session_state.overall_summary_content:
        st.markdown(st.session_state.overall_summary_content)
        # on_click에서 audio_utils의 함수를 호출하고, 고유한 파일 이름을 전달합니다.
        st.button("요약 음성 재생 ▶️", key="play_summary_content", use_container_width=True,
                  on_click=play_text_as_audio_callback, 
                  args=(st.session_state.overall_summary_content, "summary_audio.mp3"))
    else:
        st.warning("요약 내용을 불러오는 데 실패했습니다.")

    if st.session_state.get('audio_file_to_play'):
        st.audio(st.session_state.audio_file_to_play, autoplay=True)

    st.markdown("---")
    col_back_to_main, col_re_enter_profile = st.columns(2)
    with col_back_to_main:
        if st.button("이전단계", key="back_to_main_from_summary", use_container_width=True):
            st.session_state.current_page = "final_chat"
            st.session_state.overall_summary_content = ""
            st.session_state.audio_file_to_play = None
            st.rerun()
            
    with col_re_enter_profile:
        if st.button("정보 다시 입력하기", key="re_enter_profile_from_summary", use_container_width=True):
            keys_to_reset = [
                'profile_setup_completed', 'current_page', 'user_profile', 'quiz_answers',
                'current_gemini_explanation', 'last_loaded_section_key', 'current_faq_answer',
                'overall_summary_content', 'audio_file_to_play'
            ]
            for key in keys_to_reset:
                if key in st.session_state:
                    if key == 'current_page':
                        st.session_state.current_page = "profile_setup"
                    elif key == 'profile_setup_completed':
                         st.session_state.profile_setup_completed = False
                    else:
                         st.session_state[key] = None if 'audio' in key or 'summary' in key else {}
            st.rerun()