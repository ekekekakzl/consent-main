import streamlit as st
import os
import json

from config import (
    USERNAME, PASSWORD,
    SECTIONS_SIDEBAR_MAP, SECTIONS_ORDER_KEYS
)
from gemini_utils import configure_gemini, get_gemini_chat_response, get_gemini_response_from_combined_content
from ui_modules.login_page import render_login_page
from ui_modules.profile_setup_page import render_profile_setup
from ui_modules.section_page import (
    render_necessity_page, render_method_page, render_considerations_page,
    render_side_effects_page, render_precautions_page, render_self_determination_page
)
from ui_modules.final_summary_page import render_final_summary_page

st.set_page_config(layout="wide")

css_file_path = os.path.join(os.path.dirname(__file__), "style", "styles.css")
if os.path.exists(css_file_path):
    with open(css_file_path, 'r', encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning(f"CSS 파일을 찾을 수 없습니다: {css_file_path}. 기본 스타일이 적용됩니다.")

CONFIG_LOADED = False
try:
    GEMINI_API_KEY = st.secrets["gemini_api_key"]
    if configure_gemini(GEMINI_API_KEY):
        CONFIG_LOADED = True
except KeyError as e:
    st.error(f"⚠️ 설정 오류: Streamlit Secrets에서 '{e}' 키를 찾을 수 없습니다. `secrets.toml` 파일을 확인해주세요.")
except Exception as e:
    st.error(f"⚠️ Gemini API 설정 중 오류 발생: {e}")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0
if 'section_scores' not in st.session_state:
    st.session_state.section_scores = {}
if 'profile_setup_completed' not in st.session_state:
    st.session_state.profile_setup_completed = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "main"
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False
if 'all_users_data' not in st.session_state:
    st.session_state.all_users_data = []
if 'user_data' not in st.session_state:
    st.session_state.user_data = []
if 'logged_in' not in st.session_state:
    st.session_state["logged_in"] = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'current_gemini_explanation' not in st.session_state:
    st.session_state.current_gemini_explanation = ""
if 'show_quiz' not in st.session_state:
    st.session_state.show_quiz = False
if 'current_quiz_idx' not in st.session_state:
    st.session_state.current_quiz_idx = 0
if 'profile_page' not in st.session_state:
    st.session_state.profile_page = "profile_input"
if 'last_loaded_section_key' not in st.session_state:
    st.session_state.last_loaded_section_key = None
if 'current_faq_answer' not in st.session_state:
    st.session_state.current_faq_answer = ""

def render_final_chat_page():
    st.markdown("<h1 class='final-chat-title'>모든 설명을 완료했습니다! 🎉</h1>", unsafe_allow_html=True)
    st.info("이제 궁금한 점을 물어보시거나, 메인 페이지로 돌아가 다른 작업을 시작할 수 있습니다.")

    st.markdown("---")
    st.markdown("### 💬 궁금한 점을 물어보세요")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_question := st.chat_input("궁금한 점을 입력해주세요.", key="final_chat_input"):
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        with st.spinner("답변 생성 중..."):
            response = get_gemini_chat_response(st.session_state.chat_history, user_question)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
        st.rerun()

    st.markdown("---")
    col_back_to_main, col_re_enter_profile = st.columns(2)
    with col_back_to_main:
        if st.button("메인 페이지로 돌아가기", key="back_to_main_from_final_chat", use_container_width=True):
            st.session_state.current_page = "main"
            st.session_state.chat_history = []
            st.session_state.current_gemini_explanation = ""
            st.session_state.last_loaded_section_key = None
            st.session_state.show_quiz = False
            st.session_state.current_quiz_idx = 0
            st.session_state.current_faq_answer = ""
            st.rerun()
    with col_re_enter_profile:
        if st.button("환자 정보 다시 입력하기", key="re_enter_profile_from_final_chat", use_container_width=True):
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
            st.rerun()


def main():
    if not st.session_state["logged_in"]:
        render_login_page()
        return

    st.sidebar.markdown("<h2 class='sidebar-menu-title'>메뉴</h2>", unsafe_allow_html=True)

    if st.sidebar.button("👤 환자 정보 입력", key="profile_input_button"):
        st.session_state.profile_setup_completed = False
        st.session_state.current_page = "profile_setup"
        st.session_state.current_section = 1
        st.session_state.current_gemini_explanation = ""
        st.session_state.last_loaded_section_key = None
        st.session_state.show_quiz = False
        st.session_state.current_quiz_idx = 0
        st.session_state.current_faq_answer = ""
        st.rerun()

    if not st.session_state.profile_setup_completed:
        st.markdown("<h1 class='main-app-title'>로봇수술 동의서 이해 쑥쑥 설명 도우미 🤖</h1>", unsafe_allow_html=True)
        st.markdown("""
        환자분의 정보와 이해 수준을 바탕으로 기반으로, AI가 로봇수술동의서의 내용을 이해하기 쉽고 따뜻하게 설명해 드립니다.
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("나의 정보를 입력해주세요")
        st.session_state.current_page = "profile_setup"
        render_profile_setup()
    else:
        st.sidebar.markdown("---")
        st.sidebar.subheader("진행 단계")
        step_names = ["수술필요성", "수술방법", "고려사항", "부작용", "주의사항", "자기결정권"]
        
        for i, step_name in enumerate(step_names):
            page_key = SECTIONS_ORDER_KEYS[i] 

            is_active_step = False
            if st.session_state.current_page == page_key:
                is_active_step = True

            display_text = f"{i+1}. {step_name}" 
            if is_active_step:
                display_text = f"**{i+1}. {step_name}**"

            if st.sidebar.button(
                display_text,
                key=f"sidebar_step_nav_{i}",
                help=f"'{step_name}' 단계로 이동합니다.",
                on_click=lambda idx=i, pk=page_key: (
                    setattr(st.session_state, 'current_step', idx + 1),
                    setattr(st.session_state, 'current_page', pk),
                    setattr(st.session_state, 'show_quiz', False),
                    setattr(st.session_state, 'current_quiz_idx', 0),
                    setattr(st.session_state, 'current_gemini_explanation', ""),
                    setattr(st.session_state, 'last_loaded_section_key', None),
                    setattr(st.session_state, 'current_faq_answer', "")
                )
            ):
                st.rerun()
        st.sidebar.markdown("---")

        if st.sidebar.button("로그아웃", key="logout_button_sidebar"):
            st.session_state["logged_in"] = False
            st.session_state.clear()
            st.rerun()

        if st.session_state.current_page == "profile_setup":
            st.subheader("나의 정보를 입력해주세요")
            render_profile_setup()
        elif st.session_state.current_page in SECTIONS_SIDEBAR_MAP:
            current_section_key = st.session_state.current_page
            for key, info in SECTIONS_SIDEBAR_MAP.items():
                if key == current_section_key:
                    st.session_state.current_section = info["idx"]
                    break

            page_functions = {
                "necessity": render_necessity_page,
                "method": render_method_page,
                "considerations": render_considerations_page,
                "side_effects": render_side_effects_page,
                "precautions": render_precautions_page,
                "self_determination": render_self_determination_page,
            }
            page_functions[st.session_state.current_page]()
            # render_section_navigation_buttons(st.session_state.current_section) # section_page.py로 이동
        elif st.session_state.current_page == "final_chat":
            render_final_chat_page()
        elif st.session_state.current_page == "final_summary":
            render_final_summary_page()
        else:
            st.success("✅ 동의서에 대한 설명을 들어주셔서 감사합니다. 최선을 다하여 안전하게 수술하도록 하겠습니다.")
            col_re_enter, col_summarize = st.columns(2)
            with col_re_enter:
                if st.button("환자 정보 다시 입력하기", key="re_enter_profile_button", use_container_width=True):
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
                    st.rerun()
            with col_summarize:
                if st.button("전체 동의서 요약하기", key="summarize_consent_button", use_container_width=True):
                    st.session_state.current_page = "final_summary"
                    st.rerun()
            st.markdown("---")

if __name__ == "__main__":
    main()