import streamlit as st
import os
import base64 
import time

from config import (
    USERNAME, PASSWORD,
    SECTIONS_SIDEBAR_MAP, SECTIONS_ORDER_KEYS,
    IMAGE_FILE_MAP, 
    HARDCODED_BASE_EXPLANATIONS 
)

from ui_modules.login_page import render_login_page
from ui_modules.profile_setup_page import render_profile_setup

st.set_page_config(layout="wide")

css_file_path = os.path.join(os.path.dirname(__file__), "style", "styles.css")
if os.path.exists(css_file_path):
    with open(css_file_path, 'r', encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    pass

if 'logged_in' not in st.session_state:
    st.session_state["logged_in"] = False
if 'profile_setup_completed' not in st.session_state:
    st.session_state.profile_setup_completed = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = "profile_setup"
if 'audio_file_to_play' not in st.session_state:
    st.session_state.audio_file_to_play = None
if 'last_loaded_surgery_type' not in st.session_state:
    st.session_state.last_loaded_surgery_type = None
if 'last_loaded_section_key' not in st.session_state:
    st.session_state.last_loaded_section_key = None
if 'current_gemini_explanation' not in st.session_state:
    st.session_state.current_gemini_explanation = None

def set_section(key):
    st.session_state.audio_file_to_play = None
    st.session_state.current_page = key

def get_normalized_op_prefix(op_full_name):
    if "자궁" in op_full_name:
        return "uterus"
    if "전립선" in op_full_name:
        return "prostate"
    return "default"
    
def play_audio():
    section_key = st.session_state.current_page
    text_to_speak = st.session_state.get('current_gemini_explanation', '')
    
    if not text_to_speak:
        st.error("음성으로 변환할 설명 텍스트가 없습니다.")
        return
    
    op_full_name = st.session_state.user_profile.get("surgery_type", "로봇보조 자궁절제술")
    op_prefix = get_normalized_op_prefix(op_full_name) 
    
    current_dir = os.path.dirname(__file__)
    relative_path = os.path.join("static_audio", f"{op_prefix}_{section_key}.mp3")
    absolute_filename = os.path.join(current_dir, relative_path)

    if os.path.exists(absolute_filename):
        st.session_state.audio_file_to_play = absolute_filename
    else:
        st.error(f"""
        **오디오 파일 없음 오류: 파일 누락**
        
        요청 파일명: `{op_prefix}_{section_key}.mp3`
        경로: `{absolute_filename}`
        """)
        st.session_state.audio_file_to_play = None


def render_section_page(key):
    section_info = SECTIONS_SIDEBAR_MAP.get(key, {})
    section_title = section_info.get("title", "제목 없음")
    op = st.session_state.user_profile.get("surgery_type", "로봇보조 자궁절제술")
    
    if (st.session_state.get('last_loaded_section_key') != key or
        st.session_state.get('last_loaded_surgery_type') != op or
        not st.session_state.get("current_gemini_explanation")):
        
        try:
            explanation = HARDCODED_BASE_EXPLANATIONS.get(section_title, {}).get(op, "해당 섹션의 설명이 정의되지 않았습니다.")
        except AttributeError:
            explanation = "환자 프로필 정보가 부족하여 설명을 로드할 수 없습니다."
            
        st.session_state.current_gemini_explanation = explanation
        st.session_state.audio_file_to_play = None
        st.session_state.last_loaded_section_key = key
        st.session_state.last_loaded_surgery_type = op
        
    if st.session_state.audio_file_to_play and os.path.exists(st.session_state.audio_file_to_play):
        st.audio(st.session_state.audio_file_to_play, format='audio/mp3', start_time=0, autoplay=True)
        st.session_state.audio_file_to_play = None
        
    explanation_html = st.session_state.get('current_gemini_explanation', '')
    
    # 💡 [변경 1] 제목과 버튼을 한 줄에 배치하기 위해 컬럼 분할 (비율 4:1)
    col_title, col_btn = st.columns([4, 1], vertical_alignment="bottom") # vertical_alignment 옵션은 최신 Streamlit 버전 필요 (없으면 제거 가능)

    with col_title:
        st.markdown(f'<h3 class="main-app-title" style="margin-bottom:0;">{section_title}</h3>', unsafe_allow_html=True)
    
    with col_btn:
        # 여기에 "설명 듣기" 버튼 배치
        st.button("🔊 설명 듣기", on_click=play_audio, key="play_audio_button_top", use_container_width=True)

    # 간격 조정을 위한 구분선 혹은 공백 (선택 사항)
    st.write("") 

    col_img, col_content = st.columns([1.2, 1.7])
    
    with col_img:
        relative_image_path = None
        absolute_image_path = None
        current_dir = os.path.dirname(__file__) 
        
        try:
            relative_image_path = IMAGE_FILE_MAP[op][key]
            absolute_image_path = os.path.join(current_dir, relative_image_path)
            st.image(absolute_image_path, use_container_width=True)
            
        except KeyError:
            st.warning(f"이미지 경로 미정의")
            st.markdown("<div style='height: 300px; border: 1px dashed #ccc; padding: 20px; text-align: center;'>이미지 준비 중</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"이미지 로딩 실패")
            st.markdown("<div style='height: 300px; border: 1px dashed #ccc; padding: 20px; text-align: center;'>이미지 로딩 오류</div>", unsafe_allow_html=True)

    with col_content:
        st.markdown(explanation_html, unsafe_allow_html=True)

        # 💡 [변경 2] 하단 버튼 영역에서 '설명 듣기' 제거하고 2개 컬럼으로 변경
        col1, col2 = st.columns([1, 1]) # 컬럼 개수 2개로 수정

        with col1:
            current_index = SECTIONS_ORDER_KEYS.index(key)
            if current_index > 0:
                prev_key = SECTIONS_ORDER_KEYS[current_index - 1]
                if st.button("⬅️ 이전 단계", key="prev_button", use_container_width=True):
                    set_section(prev_key)
            else:
                if st.button("👤 환자 정보로 돌아가기", key="back_to_profile_button", use_container_width=True):
                    st.session_state.profile_setup_completed = False
                    st.session_state.current_page = "profile_setup"
                    st.rerun()
        
        # 중간 컬럼(오디오 버튼) 제거됨

        with col2:
            current_index = SECTIONS_ORDER_KEYS.index(key)
            if current_index < len(SECTIONS_ORDER_KEYS) - 1:
                next_key = SECTIONS_ORDER_KEYS[current_index + 1]
                st.button("다음 단계 ➡️", type="primary", key="next_button", on_click=set_section, args=(next_key,), use_container_width=True)
            else:
                st.button("설명 완료 🎉", type="primary", key="finish_button", on_click=set_section, args=("final_chat",), use_container_width=True)


def render_final_chat_page():
    st.markdown("<h1 class='final-chat-title'>모든 설명을 완료했습니다. 설명을 들어주셔서 감사합니다.</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ 이전 단계로 돌아가기", key="back_to_last_section_from_final", use_container_width=True):
            last_section_key = SECTIONS_ORDER_KEYS[-1]
            set_section(last_section_key)

    with col2:
        if st.button("👤 환자 정보로 돌아가기", key="back_to_profile_from_final", use_container_width=True, type="primary"):
            st.session_state.profile_setup_completed = False
            st.session_state.current_page = "profile_setup"
            st.rerun()


def main():
    if not st.session_state.get("logged_in"):
        render_login_page()
        return

    with st.sidebar:
        st.markdown("<h2 class='sidebar-menu-title'>메뉴</h2>", unsafe_allow_html=True)
        if st.button("👤 환자 정보 입력", key="profile_input_button", use_container_width=True):
            st.session_state.profile_setup_completed = False
            st.session_state.current_page = "profile_setup"
            st.rerun()

        if st.session_state.profile_setup_completed:
            st.markdown("---")
            st.subheader("진행 단계")
            
            for key in SECTIONS_ORDER_KEYS:
                info = SECTIONS_SIDEBAR_MAP.get(key, {"title": "오류 섹션", "idx": 0})
                is_active = st.session_state.current_page == key
                
                if st.button(str(info['idx']) + ". " + info['title'], key=f"sidebar_nav_{key}", type="primary" if is_active else "secondary", use_container_width=True):
                    set_section(key)
            
        st.markdown("---")
        if st.button("로그아웃", key="logout_button_sidebar", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    if not st.session_state.profile_setup_completed:
        st.session_state.last_loaded_section_key = None
        st.session_state.last_loaded_surgery_type = None
        st.session_state.current_gemini_explanation = None
        st.session_state.audio_file_to_play = None

        st.markdown("<h1 class='main-app-title'>로봇수술 설명 도우미 🤖</h1>", unsafe_allow_html=True)
        st.markdown("로봇수술에 대해 이해하기 쉽게 설명해 드립니다.")
        st.subheader("나의 정보를 입력해주세요")
        render_profile_setup()
    else:
        
        current_page = st.session_state.get("current_page", SECTIONS_ORDER_KEYS[0])
        
        if current_page in SECTIONS_ORDER_KEYS:
            render_section_page(current_page)
        elif current_page == "final_chat":
            render_final_chat_page()
        elif current_page == "profile_setup":
            st.subheader("나의 정보를 입력해주세요")
            render_profile_setup()
        else:
              st.session_state.current_page = "profile_setup"
              st.rerun()


if __name__ == "__main__":
    main()
