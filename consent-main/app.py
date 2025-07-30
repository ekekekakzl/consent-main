import streamlit as st
import os
import json
import base64
import time
import re

from config import (
    USERNAME, PASSWORD,
    SECTIONS_SIDEBAR_MAP, SECTIONS_ORDER_KEYS
)
from gemini_utils import configure_gemini, get_gemini_chat_response, get_gemini_response_from_combined_content, get_overall_consent_summary, synthesize_speech
from ui_modules.login_page import render_login_page
from ui_modules.profile_setup_page import render_profile_setup
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
    st.warning(f"CSS 파일을 찾을 수 없습니다: {css_file_path}. 기본 스타일이 적용됩니다.")

# Gemini API 설정
CONFIG_LOADED = False
try:
    GEMINI_API_KEY = st.secrets["gemini_api_key"]
    if configure_gemini(GEMINI_API_KEY):
        CONFIG_LOADED = True
except KeyError as e:
    st.error(f"⚠️ 설정 오류: Streamlit Secrets에서 '{e}' 키를 찾을 수 없습니다. `secrets.toml` 파일을 확인해주세요.")
except Exception as e:
    st.error(f"⚠️ Gemini API 설정 중 오류 발생: {e}")

# Streamlit Session State 초기화
# 앱이 시작될 때 한 번만 실행되어야 하는 초기화 로직
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
if 'final_chat_text_input_value' not in st.session_state:
    st.session_state.final_chat_text_input_value = ""
if 'overall_summary_content' not in st.session_state:
    st.session_state.overall_summary_content = ""
if 'current_audio_html' not in st.session_state:
    st.session_state.current_audio_html = ""

def _play_text_as_audio_callback(text_to_speak):
    """
    텍스트를 음성으로 변환하여 재생하는 콜백 함수.
    정규식을 사용하여 텍스트를 정리하고, gTTS를 통해 음성을 생성합니다.
    생성된 음성은 Base64로 인코딩되어 HTML 오디오 태그로 삽입됩니다.
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

def submit_final_chat_query():
    """
    최종 채팅 페이지에서 사용자 질문을 처리하고 Gemini 응답을 받는 콜백 함수.
    이 함수는 '전송' 버튼의 on_click 이벤트에서 호출됩니다.
    """
    user_query = st.session_state.final_chat_text_input
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.session_state.current_audio_html = "" # 새 질문 시 기존 오디오 초기화
        
        with st.spinner("답변 생성 중..."):
            response = get_gemini_chat_response(
                st.session_state.chat_history[:-1], # 현재 질문 이전의 기록 전달
                user_query,
                user_profile=st.session_state.user_profile
            )
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # 입력 필드를 비우기 위해 session_state 값을 업데이트
        st.session_state.final_chat_text_input = "" # text_input의 key와 동일하게 설정
        st.rerun() # UI를 업데이트하고 입력 필드를 비우기 위해 재실행

def render_final_chat_page():
    """
    모든 섹션 설명 완료 후 환자와 자유롭게 대화하는 페이지를 렌더링합니다.
    """
    st.markdown("<h1 class='final-chat-title'>모든 설명을 완료했습니다! 🎉</h1>", unsafe_allow_html=True)
    st.info("동의서에 대한 설명을 들어주셔서 감사합니다. 최선을 다하여 안전하게 수술하도록 하겠습니다. 궁금한 점이 있다면 편하게 물어봐주세요.")

    st.markdown("---")

    if not st.session_state.chat_history:
        st.markdown("<p style='color:#111;'>질문을 입력하여 대화를 시작해주세요.</p>", unsafe_allow_html=True)
    else:
        for i, message in enumerate(st.session_state.chat_history):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant":
                    st.button("음성 재생 ▶️", key=f"play_final_chat_{i}", use_container_width=True,
                              on_click=_play_text_as_audio_callback, args=(message["content"],))

    # 채팅 입력 필드
    # value 인자를 제거하고, key를 통해 session_state에 직접 연결되도록 합니다.
    st.text_input(
        "궁금한 점을 입력해주세요.",
        key="final_chat_text_input", # 이 key가 submit_final_chat_query에서 사용됩니다.
    )
    
    # '전송' 버튼에 콜백 함수 연결
    st.button("전송", key="final_chat_send_button", on_click=submit_final_chat_query)

    st.markdown("---")
    
    col_re_enter_profile, col_summarize = st.columns(2)
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
            st.session_state.current_faq_answer = ""
            st.session_state.current_audio_html = ""
            st.rerun()
    with col_summarize:
        if st.button("전체 동의서 요약하기", key="summarize_consent_button_from_final_chat", use_container_width=True):
            st.session_state.current_page = "final_summary"
            st.session_state.current_audio_html = ""
            st.rerun()


def render_final_summary_page():
    """
    전체 동의서 내용을 요약하여 표시하는 페이지를 렌더링합니다.
    """
    st.markdown("<h1 class='summary-title'>전체 동의서 요약 📝</h1>", unsafe_allow_html=True)
    st.info("여기에 전체 동의서의 주요 내용이 요약되어 표시될 예정입니다.")

    if not st.session_state.overall_summary_content:
        with st.spinner("AI가 전체 동의서 내용을 요약 중입니다..."):
            summary_text = get_overall_consent_summary(st.session_state.user_profile)
            st.session_state.overall_summary_content = summary_text
    
    st.markdown("---")

    if st.session_state.overall_summary_content:
        st.markdown(st.session_state.overall_summary_content)
        st.button("음성 재생 ▶️", key="play_summary_content", use_container_width=True,
                  on_click=_play_text_as_audio_callback, args=(st.session_state.overall_summary_content,))
    else:
        st.warning("요약 내용을 불러오거나 생성하는 데 문제가 발생했습니다.")

    st.markdown("---")
    col_back_to_main, col_re_enter_profile = st.columns(2)
    with col_back_to_main:
        if st.button("메인 페이지로 돌아가기", key="back_to_main_from_summary", use_container_width=True):
            st.session_state.current_page = "final_chat"
            st.session_state.chat_history = []
            st.session_state.current_gemini_explanation = ""
            st.session_state.last_loaded_section_key = None
            st.session_state.show_quiz = False
            st.session_state.current_quiz_idx = 0
            st.session_state.current_faq_answer = ""
            st.session_state.overall_summary_content = ""
            st.session_state.current_audio_html = ""
            st.rerun()
    with col_re_enter_profile:
        if st.button("환자 정보 다시 입력하기", key="re_enter_profile_from_summary", use_container_width=True):
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


def main():
    """
    Streamlit 앱의 메인 함수. 로그인, 프로필 설정, 섹션 탐색, 최종 채팅 및 요약 페이지를 관리합니다.
    """
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
        st.session_state.current_audio_html = ""
        st.rerun()

    if st.session_state.profile_setup_completed:
        st.sidebar.markdown("---")
        st.sidebar.subheader("진행 단계")
        step_names = ["수술필요성", "수술방법", "고려사항", "합병증과 관리", "주의사항", "자기결정권"]
        
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
                    setattr(st.session_state, 'current_faq_answer', ""),
                    setattr(st.session_state, 'current_audio_html', "")
                )
            ):
                st.rerun()
        st.sidebar.markdown("---")

    if st.sidebar.button("로그아웃", key="logout_button_sidebar"):
        st.session_state["logged_in"] = False
        st.session_state.clear()
        st.rerun()

    if not st.session_state.profile_setup_completed:
        st.markdown("<h1 class='main-app-title'>로봇수술 동의서 이해 쑥쑥 설명 도우미 🤖</h1>", unsafe_allow_html=True)
        st.markdown("""
        환자분의 정보와 이해 수준을 바탕으로 기반으로, AI가 로봇수술동의서의 내용을 이해하기 쉽고 따뜻하게 설명해 드립니다.
        """, unsafe_allow_html=True)
        st.subheader("나의 정보를 입력해주세요")
        render_profile_setup()
        if st.session_state.current_page == "main":
            st.session_state.current_page = "profile_setup"
    else:
        if st.session_state.current_page == "main":
            st.session_state.current_page = "final_chat"

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
        elif st.session_state.current_page == "final_chat":
            render_final_chat_page()
        elif st.session_state.current_page == "final_summary":
            render_final_summary_page()
        else:
            render_final_chat_page()

    if st.session_state.current_audio_html:
        st.markdown(st.session_state.current_audio_html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()