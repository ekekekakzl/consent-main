import streamlit as st
import os
import base64 
import time # 💡 오디오 생성 시뮬레이션에 필요한 time 모듈을 임포트합니다.

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
    """
    긴 수술명을 파일명에 사용할 짧은 영어 접두사로 정규화합니다.
    """
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
    
    # 💡 파일 경로 설정: 'static_audio' 디렉토리를 사용합니다.
    output_filename = os.path.join("static_audio", f"{op_prefix}_{section_key}.mp3")

    # 💡 파일이 존재하는지 확인합니다.
    if os.path.exists(output_filename):
        # 파일이 존재하면 바로 재생 상태로 설정합니다.
        st.session_state.audio_file_to_play = output_filename
        st.toast("🔊 오디오 파일이 준비되었습니다! (정적 파일 재생)", icon="✅")
    else:
        # 파일이 존재하지 않는 경우, 사용자에게 해당 파일이 필요함을 알립니다.
        st.error(f"""
        **오디오 파일 없음 오류:**
        
        요청하신 경로에 해당 MP3 파일을 찾을 수 없습니다. (경로: `{output_filename}`)
        
        * **해결책:** 이 애플리케이션은 정적 오디오 파일(MP3)이 미리 폴더(`static_audio/`)에 저장되어 있다고 가정합니다. 
            해당 경로에 실제 MP3 파일을 넣어주세요.
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
        
    # 💡 [START] 오디오 플레이어 위치를 상단으로 이동
    if st.session_state.audio_file_to_play and os.path.exists(st.session_state.audio_file_to_play):
        st.audio(st.session_state.audio_file_to_play, format='audio/mp3', start_time=0, autoplay=True)
        st.session_state.audio_file_to_play = None
    # 💡 [END] 오디오 플레이어 위치 이동 완료
        
    explanation_html = st.session_state.get('current_gemini_explanation', '')
    
    st.markdown(f'<h3 class="main-app-title">{section_title}</h3>', unsafe_allow_html=True)


    col_img, col_content = st.columns([1, 2.5])
    
    with col_img:
        # 💡 이미지 로딩 로직을 더 강력하게 수정하여 Streamlit 내부 오류도 잡아냅니다.
        relative_image_path = None
        absolute_image_path = None # 절대 경로 변수 추가
        
        # 💡 app.py가 실행되는 기본 경로를 먼저 확보합니다.
        current_dir = os.path.dirname(__file__) 
        
        try:
            # 1. 경로 맵에서 상대 경로를 가져옵니다. (KeyError 방지)
            relative_image_path = IMAGE_FILE_MAP[op][key]
            
            # 2. 현재 파일 위치를 기준으로 절대 경로를 구성합니다. (배포 환경에서 더 안전함)
            absolute_image_path = os.path.join(current_dir, relative_image_path)
            
            # 3. 절대 경로를 사용하여 st.image를 호출합니다.
            st.image(absolute_image_path, use_container_width=True)
            
        except KeyError:
            st.warning(f"설정 파일(config.py)에 '{op}' 수술 또는 '{key}' 섹션에 대한 **이미지 경로가 정의되어 있지 않습니다.**")
            st.markdown("<div style='height: 300px; border: 1px dashed #ccc; padding: 20px; text-align: center;'>이미지 준비 중 (경로 정의 필요)</div>", unsafe_allow_html=True)

        except Exception as e:
            # FileNotFoundError나 MediaFileStorageError 등 모든 파일 관련 오류를 처리합니다.
            error_message = f"**이미지 로딩 실패:** 경로의 파일을 찾을 수 없거나 열 수 없습니다. 오류: {e}"
            st.error(f"{error_message}")
            st.markdown("<div style='height: 300px; border: 1px dashed #ccc; padding: 20px; text-align: center;'>이미지 로딩 오류</div>", unsafe_allow_html=True)

    with col_content:
        st.markdown(explanation_html, unsafe_allow_html=True)

        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 1])

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

        with col2:
            st.button("🔊 설명 듣기", on_click=play_audio, key="play_audio_button", use_container_width=True)
        
        with col3:
            current_index = SECTIONS_ORDER_KEYS.index(key)
            if current_index < len(SECTIONS_ORDER_KEYS) - 1:
                next_key = SECTIONS_ORDER_KEYS[current_index + 1]
                st.button("다음 단계 ➡️", type="primary", key="next_button", on_click=set_section, args=(next_key,), use_container_width=True)
            else:
                st.button("설명 완료 🎉", type="primary", key="finish_button", on_click=set_section, args=("final_chat",), use_container_width=True)


def render_final_chat_page():
    st.markdown("<h1 class='final-chat-title'>모든 설명을 완료했습니다! 🎉 설명을 들어주셔서 감사합니다.</h1>", unsafe_allow_html=True)
    st.markdown("---")

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
            
            is_final = st.session_state.current_page == "final_chat"
            if st.session_state.current_page in ["final_chat"] + SECTIONS_ORDER_KEYS: 
                    st.markdown("---")
                    if st.button("✅ 전체 설명 완료", key="sidebar_nav_final", type="primary" if is_final else "secondary", use_container_width=True):
                        set_section("final_chat")

        st.markdown("---")
        if st.button("로그아웃", key="logout_button_sidebar", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    if not st.session_state.profile_setup_completed:
        st.session_state.last_loaded_section_key = None
        st.session_state.last_loaded_surgery_type = None
        st.session_state.current_gemini_explanation = None
        st.session_state.audio_file_to_play = None # 오디오 상태 초기화

        st.markdown("<h1 class='main-app-title'>로봇수술 동의서 설명 도우미 🤖</h1>", unsafe_allow_html=True)
        st.markdown("환자분의 정보를 바탕으로, 로봇수술 동의서의 내용을 이해하기 쉽게 설명해 드립니다.")
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
