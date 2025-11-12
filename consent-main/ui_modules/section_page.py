import streamlit as st
import os
import base64

from config import SECTIONS_ORDER_KEYS
from gemini_utils import get_gemini_response_from_combined_content
from ui_modules.audio_utils import play_text_as_audio_callback

def render_section_navigation_buttons(section_idx, parent_column):
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
    st.markdown("<script>window.scrollTo(0, 0);</script>", unsafe_allow_html=True)
    
    if st.session_state.get('last_loaded_section_key') != section_key:
        st.session_state.current_gemini_explanation = ""
        st.session_state.audio_file_to_play = None
    
    audio_file_path = st.session_state.get('audio_file_to_play')
    
    if audio_file_path and os.path.exists(audio_file_path):
        try:
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

            st.session_state.audio_file_to_play = None

        except Exception as e:
            st.error(f"오디오 재생 중 오류 발생: {e}")
            st.session_state.audio_file_to_play = None

    if not st.session_state.current_gemini_explanation:
        explanation = get_gemini_response_from_combined_content(
            user_profile=st.session_state.user_profile,
            current_section_title=title
        )
        st.session_state.current_gemini_explanation = explanation
    st.session_state.last_loaded_section_key = section_key

    col_left, col_right = st.columns([0.4, 0.6], gap="large")

    with col_left:
        if section_key == "method":
            img_path = os.path.join(os.path.dirname(__file__), "..", "images", "로봇수술이미지.png")
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
                st.button("음성 재생 ▶️", key=f"play_section_explanation_{section_key}", use_container_width=True,
                            on_click=play_text_as_audio_callback, 
                            args=(st.session_state.current_gemini_explanation, f"section_audio_{section_key}.mp3"))

        explanation_text = st.session_state.get('current_gemini_explanation', '')
        if explanation_text:
            st.markdown(explanation_text, unsafe_allow_html=True)
        
        st.markdown("---")
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