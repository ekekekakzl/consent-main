import streamlit as st
import os
import base64
# [❗️수정] sys 모듈 및 os 모듈을 사용하여 루트 디렉토리를 임포트 경로에 추가합니다.
import sys
# 현재 파일의 상위 디렉토리(루트 디렉토리)를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import SECTIONS_ORDER_KEYS
from gemini_utils import get_gemini_response_from_combined_content
# [❗️수정] sys.path를 설정했으므로, 이제 audio_util을 직접 임포트할 수 있습니다.
from audio_util import play_audio_button 


# [❗️제거] BASE_AUDIO_PATH는 이제 audio_util.py에서 관리합니다.
# BASE_AUDIO_PATH = "/tmp"

# [❗️제거] _on_tts_click 함수는 제거합니다.

def _render_section_navigation_buttons_inline(section_idx):
    """
    네비게이션 버튼을 인라인으로 렌더링합니다. 
    """
    current_page_key = st.session_state.current_page
    current_page_key_index = SECTIONS_ORDER_KEYS.index(current_page_key)

    # 네비게이션 버튼을 위한 3개의 컬럼을 생성합니다.
    nav_cols = st.columns([1, 1, 1])

    # 이전 단계 버튼
    with nav_cols[0]:
        if current_page_key_index > 0:
            if st.button("⬅️ 이전 단계", key=f"prev_section_{section_idx}", use_container_width=True):
                st.session_state.current_page = SECTIONS_ORDER_KEYS[current_page_key_index - 1]
                st.rerun()
        else:
            if st.button("⬅️ 이전 단계", key=f"back_to_profile_{section_idx}", use_container_width=True):
                st.session_state.profile_setup_completed = False
                st.session_state.current_page = "profile_setup"
                st.rerun()

    # (중앙 컬럼은 비워둡니다)

    # 다음 단계 / 완료 버튼
    with nav_cols[2]:
        if current_page_key_index < len(SECTIONS_ORDER_KEYS) - 1:
            if st.button("다음 단계 ➡️", key=f"next_section_{section_idx}", use_container_width=True, type="primary"):
                st.session_state.current_page = SECTIONS_ORDER_KEYS[current_page_key_index + 1]
                st.rerun()
        else:
            if st.button("설명 완료 ✅", key=f"finish_sections", use_container_width=True, type="primary"):
                st.session_state.current_page = "final_chat"
                st.rerun()


def render_section_page(section_idx, title, description, section_key):
    st.markdown("<script>window.scrollTo(0, 0);</script>", unsafe_allow_html=True)
    
    # 1. 콘텐츠 초기화
    # 섹션이 변경되면 이전 텍스트와 오디오 파일을 지웁니다.
    if st.session_state.get('last_loaded_section_key') != section_key:
        st.session_state.current_gemini_explanation = ""
        # [❗️제거] 오디오 재생 요청 상태 리셋 코드는 audio_util.py 내부에서 관리됩니다.
        # st.session_state.audio_file_to_play = None
    
    # 2. 오디오 파일 재생 로직 (audio_util.py가 모든 것을 처리하도록 변경)
    # st.session_state.get('audio_file_to_play') 관련 로직을 제거합니다.
    
    # 3. 텍스트 생성
    if not st.session_state.get('current_gemini_explanation'):
        explanation = get_gemini_response_from_combined_content(
            user_profile=st.session_state.user_profile,
            current_section_title=title
        )
        st.session_state.current_gemini_explanation = explanation
    st.session_state.last_loaded_section_key = section_key

    # 4. 레이아웃
    col_left, col_right = st.columns([0.4, 0.6], gap="large")

    with col_left:
        if section_key == "method":
            # [❗️수정] os.path.join에 os.path.dirname(os.path.abspath(__file__))을 사용하지 않고, 
            # app.py와 section_page.py가 동일한 계층에 있다고 가정하고 상대 경로를 사용합니다.
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images", "로봇수술이미지.png")
            # 경로가 너무 복잡하면 Streamlit 환경에서 찾기 어려울 수 있으므로, 
            # 임시로 이미지 파일을 찾을 수 없는 경우를 대비하여 경로 탐색 로직을 추가했습니다.
            
            # `ui_modules` 폴더 기준으로 상위 폴더의 `images`를 찾습니다.
            relative_img_path = os.path.join(os.path.dirname(__file__), "..", "images", "로봇수술이미지.png")
            
            if os.path.exists(relative_img_path):
                st.image(relative_img_path, caption="[로봇수술 시스템 구성 요소]", use_container_width=True)
            else:
                # 파일이 없을 경우, Streamlit 앱의 루트 경로에서 다시 시도해봅니다.
                alt_img_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images", "로봇수술이미지.png")
                if os.path.exists(alt_img_path):
                     st.image(alt_img_path, caption="[로봇수술 시스템 구성 요소]", use_container_width=True)
                else:
                    st.warning(f"이미지 파일을 찾을 수 없습니다: {relative_img_path} 또는 {alt_img_path}")
        else:
            st.empty()

    with col_right:
        title_col, play_col = st.columns([0.6, 0.4])
        with title_col:
            st.markdown(f"### {title}")
            st.caption(description)
        with play_col:
            if st.session_state.current_gemini_explanation:
                # [❗️수정] audio_util.play_audio_button 함수를 직접 호출합니다.
                # 이 함수가 버튼 렌더링, 오디오 생성, 재생 위젯 표시까지 모두 처리합니다.
                play_audio_button(
                    raw_html_content=st.session_state.current_gemini_explanation,
                    key=f"play_section_explanation_{section_key}"
                )

        explanation_text = st.session_state.get('current_gemini_explanation', '')
        if explanation_text:
            st.markdown(explanation_text, unsafe_allow_html=True)
        
        st.markdown("---")
    
    # 네비게이션 버튼을 전체 메인 영역 하단에 독립적으로 렌더링합니다.
    _render_section_navigation_buttons_inline(section_idx)


def render_necessity_page():
    render_section_page(1, "필요성", "[왜 수술을 해야 하나요?]", "necessity")

def render_method_page():
    render_section_page(2, "방법", "[로봇수술은 어떻게 진행되나요?]", "method")

def render_considerations_page():
    render_section_page(3, "고려 사항", "[알아두어야 할 점] ", "considerations")

def render_side_effects_page():
    render_section_page(4, "합병증", "[생길 수 있는 합병증]", "side_effects")

def render_precautions_page():
    render_section_page(5, "수술 후 관리", "[생활 관리 방법]", "precautions")

