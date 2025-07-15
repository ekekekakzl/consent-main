import streamlit as st
import os
import json # session_state를 위한 import 유지

# 분리된 모듈에서 필요한 함수와 상수를 임포트
from config import (
    EXCEL_FILE_PATH, USERNAME, PASSWORD,
    SECTIONS_SIDEBAR_MAP, SECTIONS_ORDER_KEYS
)
from data_loader import load_excel_data
from gemini_utils import configure_gemini
from ui_modules.login_page import render_login_page
from ui_modules.profile_setup_page import render_profile_setup
from ui_modules.section_page import (
    render_necessity_page, render_method_page, render_considerations_page,
    render_side_effects_page, render_precautions_page, render_self_determination_page
)

# --- 페이지 설정 ---
st.set_page_config(layout="wide")

# --- 커스텀 CSS 로드 및 적용 ---
# style/styles.css 파일의 경로를 정확히 지정
css_file_path = os.path.join(os.path.dirname(__file__), "style", "styles.css")
if os.path.exists(css_file_path):
    # 파일을 읽을 때 인코딩을 'utf-8'로 명시합니다.
    with open(css_file_path, 'r', encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning(f"CSS 파일을 찾을 수 없습니다: {css_file_path}. 기본 스타일이 적용됩니다.")

# --- 1. Streamlit Secrets에서 설정 변수 로드 및 Gemini API 설정 ---
CONFIG_LOADED = False
try:
    GEMINI_API_KEY = st.secrets["gemini_api_key"]
    if configure_gemini(GEMINI_API_KEY):
        CONFIG_LOADED = True
except KeyError as e:
    st.error(f"⚠️ 설정 오류: Streamlit Secrets에서 '{e}' 키를 찾을 수 없습니다. `secrets.toml` 파일을 확인해주세요.")
except Exception as e:
    st.error(f"⚠️ 설정 오류: {e}")


# --- 2. 세션 상태 초기화 ---
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


# --- 엑셀 파일은 앱 시작 시 한 번만 로드하여 세션 상태에 저장 ---
if 'excel_data_dict' not in st.session_state:
    st.session_state.excel_data_dict = load_excel_data(EXCEL_FILE_PATH)


# --- Main App Logic ---
def main():
    if not st.session_state["logged_in"]:
        render_login_page()
        return

    st.sidebar.title("메뉴")

    # 사이드바에 진행 단계 네비게이션 추가
    step_names = ["환자정보", "수술필요성", "수술방법", "고려사항", "부작용", "주의사항", "자기결정권"]
    st.sidebar.subheader("진행 단계")
    for i, step_name in enumerate(step_names):
        # 네비게이션을 위한 페이지 키 결정
        if i == 0:
            page_key = "profile_setup"
        else:
            page_key = SECTIONS_ORDER_KEYS[i-1] # SECTIONS_ORDER_KEYS는 0번 인덱스부터 시작

        # 현재 활성화된 단계인지 확인하여 텍스트를 굵게 표시
        is_active_step = False
        if st.session_state.current_page == page_key:
            if page_key == "profile_setup" and st.session_state.current_step == 1:
                is_active_step = True
            # 현재 섹션 인덱스와 단계 인덱스가 일치하는지 확인
            elif page_key != "profile_setup" and st.session_state.current_section == (i + 1):
                is_active_step = True

        display_text = f"{i+1}. {step_name}"
        if is_active_step:
            display_text = f"**{i+1}. {step_name}**" # 활성화된 단계는 굵게 표시

        if st.sidebar.button(
            display_text,
            key=f"sidebar_step_nav_{i}",
            help=f"'{step_name}' 단계로 이동합니다.",
            on_click=lambda idx=i, pk=page_key: (
                setattr(st.session_state, 'current_step', idx + 1),
                setattr(st.session_state, 'current_page', pk),
                setattr(st.session_state, 'show_quiz', False),
                setattr(st.session_state, 'current_quiz_idx', 0)
            )
        ):
            st.rerun()

    st.sidebar.markdown("---") # 진행 단계와 다음 메뉴 사이 구분선
    # '로그아웃' 버튼 key 수정
    if st.sidebar.button("로그아웃", key="logout_button_sidebar"):
        st.session_state["logged_in"] = False
        st.session_state.clear()
        st.rerun()

    if st.session_state.excel_data_dict is None:
        st.title("🚨 오류: 엑셀 파일 로드 실패 �")
        st.error("애플리케이션을 시작하는 데 필요한 엑셀 동의서 파일을 찾거나 읽을 수 없습니다.")
        st.info(f"'{EXCEL_FILE_PATH}' 경로에 파일이 올바르게 위치해 있는지 확인하고, 파일 형식이 올바른지 확인해주세요.")
        return

    # 페이지 라우팅
    if st.session_state.current_page == "profile_setup":
        render_profile_setup()
    elif st.session_state.profile_setup_completed and st.session_state.current_page in SECTIONS_SIDEBAR_MAP:
        # 각 섹션 페이지 함수를 매핑하여 호출
        page_functions = {
            "necessity": render_necessity_page,
            "method": render_method_page,
            "considerations": render_considerations_page,
            "side_effects": render_side_effects_page,
            "precautions": render_precautions_page,
            "self_determination": render_self_determination_page,
        }
        page_functions[st.session_state.current_page]()
    else:
        st.title("환자 맞춤형 로봇수술 동의서 이해쑥쑥 설명 도우미 🤖")
        st.markdown("""
        환자분의 정보와 동의서 내용을 기반으로, AI가 이해하기 쉽고 따뜻하게 설명해 드립니다.
        """, unsafe_allow_html=True)
        
        if not st.session_state.profile_setup_completed:
            st.markdown("---")
            st.subheader("나의 정보를 입력해주세요")
            st.session_state.current_page = "profile_setup"
            st.session_state.current_section = 1
            render_profile_setup()
        else:
            st.success("✅ 동의서에 대한 설명을 들어주셔서 감사합니다. 최선을 다하여 안전하게 수술하도록 하겠습니다.")

if __name__ == "__main__":
    main()
