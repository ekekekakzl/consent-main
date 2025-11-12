import streamlit as st
import os
# QUIZ_DATA와 FAQ_DATA 임포트 제거
from config import SECTIONS_ORDER_KEYS
from gemini_utils import get_gemini_response_from_combined_content
# 새로 만든 오디오 유틸리티 파일에서 콜백 함수를 가져옵니다.
from ui_modules.audio_utils import play_text_as_audio_callback

def render_section_navigation_buttons(section_idx, parent_column):
    """
    섹션 간 이동을 위한 '이전 단계' 및 '다음 단계' 버튼을 렌더링합니다.
    """
    current_page_key = st.session_state.current_page
    current_page_key_index = SECTIONS_ORDER_KEYS.index(current_page_key)

    with parent_column:
        nav_cols = st.columns(2)
        with nav_cols[0]:
            if current_page_key_index > 0:
                if st.button("이전 단계", key=f"prev_section_{section_idx}", use_container_width=True):
                    st.session_state.current_page = SECTIONS_ORDER_KEYS[current_page_key_index - 1]
                    st.rerun()
            else:
                if st.button("이전 단계", key=f"back_to_profile_{section_idx}", use_container_width=True):
                    st.session_state.profile_setup_completed = False
                    st.session_state.current_page = "profile_setup"
                    st.rerun()

        with nav_cols[1]:
            if current_page_key_index < len(SECTIONS_ORDER_KEYS) - 1:
                if st.button("다음 단계", key=f"next_section_{section_idx}", use_container_width=True, type="primary"):
                    st.session_state.current_page = SECTIONS_ORDER_KEYS[current_page_key_index + 1]
                    st.rerun()
            else:
                if st.button("설명 완료", key=f"finish_sections", use_container_width=True, type="primary"):
                    st.session_state.current_page = "final_chat"
                    st.rerun()

def render_section_page(section_idx, title, description, section_key):
    """
    각 동의서 섹션 페이지를 렌더링하는 핵심 함수.
    """
    # 페이지가 로드될 때마다 스크롤을 맨 위로 이동시킵니다.
    st.markdown("<script>window.scrollTo(0, 0);</script>", unsafe_allow_html=True)
    
    # [수정] 로직 순서 변경:
    # 새 섹션으로 이동했는지 먼저 확인하고, audio_file_to_play 상태를 None으로 설정합니다.
    # 이 로직이 st.audio() 렌더링보다 먼저 실행되어야 합니다.
    if st.session_state.get('last_loaded_section_key') != section_key:
        st.session_state.current_gemini_explanation = ""
        # 퀴즈와 FAQ 관련 세션 상태 초기화 코드 제거
        # [수정] 새 섹션으로 이동하면, 이전 섹션의 오디오 플레이어를 숨깁니다.
        st.session_state.audio_file_to_play = None
    
    # [수정] 오디오 플레이어를 페이지 최상단에서 렌더링합니다.
    # 'audio_file_to_play' 상태가 None이 아닌 경우에만 렌더링됩니다.
    if st.session_state.get('audio_file_to_play'):
        st.audio(st.session_state.audio_file_to_play, autoplay=True)
        # [수정] 플레이어가 계속 떠 있도록 이 줄은 주석 처리 상태를 유지합니다.
        # st.session_state.audio_file_to_play = None

    if not st.session_state.current_gemini_explanation:
        explanation = get_gemini_response_from_combined_content(
            user_profile=st.session_state.user_profile,
            current_section_title=title
        )
        st.session_state.current_gemini_explanation = explanation
    st.session_state.last_loaded_section_key = section_key

    # 컬럼 정의를 [0.4, 0.6]으로 변경합니다. (이미지 왼쪽, 나머지 오른쪽)
    col_left, col_right = st.columns([0.4, 0.6], gap="large")

    # col_left (왼쪽 컬럼): 이미지만 표시
    with col_left:
        if section_key == "method":
            img_path = os.path.join(os.path.dirname(__file__), "../images/로봇수술이미지.png")
            if os.path.exists(img_path):
                st.image(img_path, caption="[로봇수술 시스템 구성 요소]", use_container_width=True)
        else:
            # 다른 페이지에서는 이 컬럼을 비워둡니다.
            st.empty()

    # col_right (오른쪽 컬럼): 설명과 네비게이션 버튼
    with col_right:
        # --- 설명 부분 ---
        title_col, play_col = st.columns([0.6, 0.4])
        with title_col:
            st.markdown(f"### {title}")
            st.caption(description)
        with play_col:
            if st.session_state.current_gemini_explanation:
                st.button("음성 재생 ▶️", key=f"play_section_explanation_{section_key}", use_container_width=True,
                            on_click=play_text_as_audio_callback, 
                            args=(st.session_state.current_gemini_explanation, f"section_audio_{section_key}.mp3"))

        # 이미지 로직은 col_left로 이동했으므로 여기서는 제거됩니다.

        explanation_text = st.session_state.get('current_gemini_explanation', '')
        if explanation_text:
            st.markdown(explanation_text, unsafe_allow_html=True)
        
        # [수정] st.audio() 렌더링 로직은 페이지 최상단으로 이동했습니다.
        
        # --- 네비게이션 버튼 부분 ---
        st.markdown("---") # 구분선 추가
        render_section_navigation_buttons(section_idx, col_right)


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