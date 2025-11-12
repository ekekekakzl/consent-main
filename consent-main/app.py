import streamlit as st
import os
import sys

# [❗️추가] 프로젝트 루트 디렉토리를 sys.path에 추가하여
# 서브 모듈(ui_modules/*)이 루트의 모듈(config.py, audio_util.py)을 
# 안정적으로 임포트할 수 있도록 합니다.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)


# 프로젝트의 다른 모듈들을 임포트합니다.
from config import (
    USERNAME, PASSWORD,
    SECTIONS_SIDEBAR_MAP, SECTIONS_ORDER_KEYS
)

from ui_modules.login_page import render_login_page
from ui_modules.profile_setup_page import render_profile_setup
# 'render_self_determination_page' 임포트 제거
from ui_modules.section_page import (
    render_necessity_page, render_method_page, render_considerations_page,
    render_side_effects_page, render_precautions_page
)

st.set_page_config(layout="wide")

# CSS 파일 로드
css_file_path = os.path.join(os.path.dirname(__file__), "style", "styles.css")
if os.path.exists(css_file_path):
    with open(css_file_path, 'r', encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning(f"CSS 파일을 찾을 수 없습니다: {css_file_path}")

# [수정] Gemini API 키 설정 및 모델 관련 코드 제거

# Streamlit Session State 초기화
if 'logged_in' not in st.session_state:
    st.session_state["logged_in"] = False
if 'profile_setup_completed' not in st.session_state:
    st.session_state.profile_setup_completed = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = "profile_setup"
# [❗️수정] 'audio_file_to_play' 초기화 코드를 제거합니다.
# if 'audio_file_to_play' not in st.session_state:
#     st.session_state.audio_file_to_play = None


def render_final_chat_page():
    """
    모든 섹션 설명 완료 후 최종 페이지를 렌더링합니다.
    """
    st.markdown("<h1 class='final-chat-title'>모든 설명을 완료했습니다! 🎉 설명을 들어주셔서 감사합니다.</h1>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("이전 단계로 돌아가기", key="back_to_last_section_from_final", use_container_width=True):
            last_section_key = SECTIONS_ORDER_KEYS[-1]
            st.session_state.current_page = last_section_key
            st.rerun()

    with col2:
        if st.button("환자 정보로 돌아가기", key="back_to_profile_from_final", use_container_width=True):
            st.session_state.profile_setup_completed = False
            st.session_state.current_page = "profile_setup"
            st.rerun()

def main():
    """
    Streamlit 앱의 메인 함수. 페이지 라우팅 및 상태 관리를 담당합니다.
    """
    if not st.session_state.get("logged_in"):
        render_login_page()
        return

    # [수정] Gemini 모델 초기화 로직 제거

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
        # 'self_determination' 항목 제거
        page_functions = {
            "necessity": render_necessity_page,
            "method": render_method_page,
            "considerations": render_considerations_page,
            "side_effects": render_side_effects_page,
            "precautions": render_precautions_page,
        }
        
        current_page = st.session_state.get("current_page", "profile_setup")
        
        if current_page in page_functions:
            page_functions[current_page]()
        elif current_page == "profile_setup":
            st.subheader("나의 정보를 입력해주세요")
            render_profile_setup()
        # [수정] 'else:' 대신 'elif'를 사용하여 명시적으로 final_chat 페이지를 확인합니다.
        elif current_page == "final_chat":
            render_final_chat_page()
        else:
            # 예기치 않은 페이지 상태일 경우 기본 페이지로 리디렉션
            st.session_state.current_page = "profile_setup"
            st.rerun()

if __name__ == "__main__":
    main()
