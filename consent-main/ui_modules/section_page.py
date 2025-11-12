import streamlit as st
import os
import base64
# import datetime # datetime은 현재 사용되지 않으므로 제거합니다.
# from io import BytesIO # BytesIO는 현재 사용되지 않으므로 제거합니다.

from config import SECTIONS_ORDER_KEYS
from gemini_utils import get_gemini_response_from_combined_content
from ui_modules.audio_utils import play_text_as_audio_callback

# [❗️유지] Streamlit Cloud에서 안정적인 파일 경로
BASE_AUDIO_PATH = "/tmp"

def _on_tts_click(text_to_speak, section_key):
    """
    [❗️추가] 음성 재생 버튼 클릭 시 호출되는 콜백 함수.
    audio_utils를 호출하고, 성공 시 st.session_state에 경로를 저장합니다.
    """
    # 1. 절대 경로 파일 이름 생성 (현재 페이지, 타임스탬프 대신 고유 ID 사용)
    # Streamlit은 새로고침 시 파일명을 기억할 필요가 없으므로 UUID를 사용해 중복 방지
    audio_file_name = f"tts_output_{section_key}_{os.urandom(8).hex()}.mp3"
    audio_file_path = os.path.join(BASE_AUDIO_PATH, audio_file_name)

    # 2. 오디오 생성 및 파일 경로 반환
    generated_file_path = play_text_as_audio_callback(
        text_to_speak=text_to_speak, 
        output_filename=audio_file_path
    )
    
    # 3. 세션 상태에 저장 (다음 렌더링 시 재생되도록)
    if generated_file_path:
        st.session_state.audio_file_to_play = generated_file_path
    else:
        st.session_state.audio_file_to_play = None


def _render_section_navigation_buttons_inline(section_idx):
    """
    [❗️수정] 네비게이션 버튼을 인라인으로 렌더링합니다. 
    기존의 render_section_navigation_buttons 함수를 인라인으로 변경하고, 
    외부에서 컬럼을 전달받지 않도록 수정했습니다.
    """
    current_page_key = st.session_state.current_page
    current_page_key_index = SECTIONS_ORDER_KEYS.index(current_page_key)

    # [❗️수정] 여기서 st.columns를 호출하여 네비게이션 버튼을 위한 3개의 컬럼을 생성합니다.
    # play_col 내부가 아닌, render_section_page의 하단에 배치하기 위해 함수를 분리했습니다.
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
        # 오디오 재생 요청 상태도 리셋합니다.
        st.session_state.audio_file_to_play = None
    
    # 2. 오디오 파일 재생 로직 (초기화된 세션 상태를 확인)
    audio_file_path = st.session_state.get('audio_file_to_play')
    
    if audio_file_path and os.path.exists(audio_file_path):
        try:
            # 파일을 읽고 Base64 인코딩
            with open(audio_file_path, "rb") as f:
                data = f.read()
            
            b64 = base64.b64encode(data).decode()
            
            md = f"""
                <audio controls autoplay="true">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                Your browser does not support the audio element.
                </audio>
                """
            
            st.markdown(md, unsafe_allow_html=True)

            # 재생이 끝나면 파일 경로와 실제 파일을 삭제합니다.
            st.session_state.audio_file_to_play = None
            os.remove(audio_file_path) # [❗️추가] 재생 후 임시 파일 삭제

        except Exception as e:
            st.error(f"오디오 재생 중 오류 발생: {e}")
            st.session_state.audio_file_to_play = None
            if os.path.exists(audio_file_path):
                 os.remove(audio_file_path)

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
            # [❗️수정] os.path.join에 os.path.dirname(__file__) 사용 방식 수정
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images", "로봇수술이미지.png")
            if os.path.exists(img_path):
                st.image(img_path, caption="[로봇수술 시스템 구성 요소]", use_container_width=True)
            else:
                st.warning(f"이미지 파일을 찾을 수 없습니다: {img_path}")
        else:
            st.empty()

    with col_right:
        title_col, play_col = st.columns([0.6, 0.4])
        with title_col:
            st.markdown(f"### {title}")
            st.caption(description)
        with play_col:
            if st.session_state.current_gemini_explanation:
                # [❗️수정] on_click에 콜백 함수(_on_tts_click)와 인자 추가
                st.button("음성 재생 ▶️", key=f"play_section_explanation_{section_key}", use_container_width=True,
                            on_click=_on_tts_click, 
                            args=(st.session_state.current_gemini_explanation, section_key))

        explanation_text = st.session_state.get('current_gemini_explanation', '')
        if explanation_text:
            st.markdown(explanation_text, unsafe_allow_html=True)
        
        st.markdown("---")
        # [❗️수정] 네비게이션 버튼 렌더링을 col_right의 영역을 벗어나서 독립적으로 호출합니다.
    
    # [❗️수정] 네비게이션 버튼을 전체 메인 영역 하단에 독립적으로 렌더링합니다.
    # 이렇게 해야 st.columns 중첩 오류가 발생하지 않습니다.
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
