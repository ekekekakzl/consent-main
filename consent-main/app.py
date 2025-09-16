import streamlit as st
import os
import google.generativeai as genai

# 프로젝트의 다른 모듈들을 임포트합니다.
from config import (
    USERNAME, PASSWORD,
    SECTIONS_SIDEBAR_MAP, SECTIONS_ORDER_KEYS
)
# gemini_utils는 음성 합성 기능이 없으므로 해당 함수는 제거합니다.
from gemini_utils import configure_gemini, get_overall_consent_summary, get_gemini_response_from_combined_content
from ui_modules.login_page import render_login_page
from ui_modules.profile_setup_page import render_profile_setup
# ui_modules.section_page에서 각 페이지 렌더링 함수를 가져옵니다.
from ui_modules.section_page import (
    render_necessity_page, render_method_page, render_considerations_page,
    render_side_effects_page, render_precautions_page, render_self_determination_page
)
from ui_modules.final_summary_page import render_final_summary_page

st.set_page_config(layout="wide")

# CSS 파일 로드
css_file_path = os.path.join(os.path.dirname(__file__), "style", "styles.css")
if os.path.exists(css_file_path):
    with open(css_file_path, 'r', encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning(f"CSS 파일을 찾을 수 없습니다: {css_file_path}")

# Gemini API 키 설정
try:
    GEMINI_API_KEY = st.secrets["gemini_api_key"]
    genai.configure(api_key=GEMINI_API_KEY)
except KeyError as e:
    st.error(f"⚠️ 설정 오류: Streamlit Secrets에서 '{e}' 키를 찾을 수 없습니다.")
except Exception as e:
    st.error(f"⚠️ Gemini API 설정 중 오류 발생: {e}")

# Streamlit Session State 초기화
if 'logged_in' not in st.session_state:
    st.session_state["logged_in"] = False
if 'profile_setup_completed' not in st.session_state:
    st.session_state.profile_setup_completed = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = "profile_setup"
if 'model' not in st.session_state:
    st.session_state.model = None
if 'current_gemini_explanation' not in st.session_state:
    st.session_state.current_gemini_explanation = ""
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'last_loaded_section_key' not in st.session_state:
    st.session_state.last_loaded_section_key = None
if 'current_faq_answer' not in st.session_state:
    st.session_state.current_faq_answer = ""
if 'overall_summary_content' not in st.session_state:
    st.session_state.overall_summary_content = ""
# [수정] edge-tts는 파일 기반이므로 audio_file_to_play 상태를 사용합니다.
if 'audio_file_to_play' not in st.session_state:
    st.session_state.audio_file_to_play = None


def render_final_chat_page():
    """
    모든 섹션 설명 완료 후 최종 페이지를 렌더링합니다.
    """
    st.markdown("<h1 class='final-chat-title'>모든 설명을 완료했습니다! 🎉</h1>", unsafe_allow_html=True)
    st.info("동의서에 대한 설명을 들어주셔서 감사합니다. 추가적으로 궁금한 점이 있다면 의료진에게 편하게 질문해주세요.")
    st.markdown("---")

    col_back_to_last_section, col_summarize = st.columns(2)
    with col_back_to_last_section:
        if st.button("이전 단계", key="back_to_last_section_from_final", use_container_width=True):
            last_section_key = SECTIONS_ORDER_KEYS[-1]
            st.session_state.current_page = last_section_key
            st.rerun()
    with col_summarize:
        if st.button("전체 동의서 요약하기", key="summarize_consent_button_from_final_chat", use_container_width=True):
            st.session_state.current_page = "final_summary"
            # [수정] 페이지 이동 시 오디오 상태를 초기화합니다.
            st.session_state.audio_file_to_play = None 
            st.rerun()

def main():
    """
    Streamlit 앱의 메인 함수. 페이지 라우팅 및 상태 관리를 담당합니다.
    """
    if not st.session_state.get("logged_in"):
        render_login_page()
        return

    if st.session_state.profile_setup_completed and st.session_state.model is None:
        if st.session_state.user_profile:
            st.session_state.model = configure_gemini(st.session_state.user_profile)
            if st.session_state.model is None:
                st.error("응답 모델을 초기화하는 데 실패했습니다.")
                return
        else:
            st.error("사용자 정보를 불러오는 데 실패했습니다.")
            st.session_state.profile_setup_completed = False
            st.session_state.current_page = "profile_setup"
            st.rerun()
            return

    # 사이드바 렌더링
    with st.sidebar:
        st.markdown("<h2 class='sidebar-menu-title'>메뉴</h2>", unsafe_allow_html=True)
        if st.button("👤 환자 정보 입력", key="profile_input_button"):
            st.session_state.profile_setup_completed = False
            st.session_state.current_page = "profile_setup"
            st.rerun()

        if st.session_state.profile_setup_completed:
            st.markdown("---")
            st.subheader("진행 단계")
            for key, info in SECTIONS_SIDEBAR_MAP.items():
                is_active = st.session_state.current_page == key
                label = f"**{info['idx']}. {info['title']}**" if is_active else f"{info['idx']}. {info['title']}"
                if st.button(label, key=f"sidebar_nav_{key}"):
                    st.session_state.current_page = key
                    st.rerun()
        
        st.markdown("---")
        if st.button("로그아웃", key="logout_button_sidebar"):
            st.session_state.clear()
            st.rerun()

    # 메인 페이지 콘텐츠 라우팅
    if not st.session_state.profile_setup_completed:
        st.markdown("<h1 class='main-app-title'>로봇수술 동의서 설명 도우미 🤖</h1>", unsafe_allow_html=True)
        st.markdown("환자분의 정보를 바탕으로, 로봇수술 동의서의 내용을 이해하기 쉽게 설명해 드립니다.")
        st.subheader("나의 정보를 입력해주세요")
        render_profile_setup()
    else:
        page_functions = {
            "necessity": render_necessity_page,
            "method": render_method_page,
            "considerations": render_considerations_page,
            "side_effects": render_side_effects_page,
            "precautions": render_precautions_page,
            "self_determination": render_self_determination_page,
        }
        
        current_page = st.session_state.get("current_page", "profile_setup")
        
        if current_page in page_functions:
            page_functions[current_page]()
        elif current_page == "final_summary":
            render_final_summary_page()
        elif current_page == "profile_setup":
            st.subheader("나의 정보를 입력해주세요")
            render_profile_setup()
        else:
            render_final_chat_page()

    # [제거] 오디오 플레이어는 이제 각 페이지 내부에서 렌더링되므로 이 코드는 필요 없습니다.

if __name__ == "__main__":
    main()