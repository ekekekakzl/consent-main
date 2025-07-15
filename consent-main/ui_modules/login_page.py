import streamlit as st
import os
from config import USERNAME, PASSWORD

def render_login_page():
    st.title("")
    img_path = os.path.join(os.path.dirname(__file__), "../images/robot_doctor_logo.png") # 이미지 경로 수정
    
    # 메인 컬럼 비율 조정 (전체 폼의 중앙 위치는 크게 변경하지 않음)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2: # 로그인 폼이 들어갈 중앙 컬럼
        # 이미지와 제목을 위한 하위 컬럼 생성
        # 왼쪽 여백을 위한 빈 컬럼을 추가하여 그림과 글씨를 왼쪽으로 밀어냅니다.
        # [왼쪽 빈 공간, 이미지 컬럼, 제목 컬럼]
        empty_left_sub_col, img_col, title_col = st.columns([0.3, 0.5, 2]) # 비율 조정: 0.2만큼 왼쪽으로 이동
        
        with img_col:
            if os.path.exists(img_path):
                st.image(img_path, width=400, use_container_width=False) # 이미지 크기 조정
            else:
                st.warning(f"이미지 파일을 찾을 수 없습니다: {img_path}")
                st.image("https://via.placeholder.com/100", width=100, use_container_width=False) # 대체 이미지
        
        with title_col:
            # 제목을 이미지 옆에 배치하기 위해 margin-left를 0으로 유지하고 text-align을 제거
            # margin-top을 추가하여 글씨를 아래로 내립니다.
            st.markdown('<h2 style="margin-bottom: 1.5rem; margin-top: 2rem;">로봇수술동의서 이해쑥쑥</h2>', unsafe_allow_html=True)
            
        username = st.text_input("아이디", key="login_username")
        # st.text.input을 st.text_input으로 수정
        password = st.text_input("비밀번호", type="password", key="login_password")
        login_btn = st.button("로그인", key="login_button", use_container_width=True)
    
        if login_btn:
            if username == USERNAME and password == PASSWORD:
                st.session_state["logged_in"] = True
                st.success("로그인 성공!")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")