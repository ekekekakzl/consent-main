import streamlit as st

def render_profile_setup():
    """
    사용자로부터 '수술명'만 입력받는 페이지를 렌더링합니다.
    """
    with st.form("profile_form"):
        
        surgery_options = ["선택하세요", "로봇보조 자궁절제술", "로봇보조 전립선절제술"]
        
        current_surgery_value = st.session_state.user_profile.get('surgery', "선택하세요")
        current_surgery_index = surgery_options.index(current_surgery_value) if current_surgery_value in surgery_options else 0

        surgery = st.selectbox(
            label="수술명 *",
            options=surgery_options,
            index=current_surgery_index
        )
        
        submitted = st.form_submit_button("설명 듣기 시작 >")
    
    # "설명 듣기 시작 >" 버튼이 클릭되었을 때 실행될 로직
    if submitted:
        # 수술명이 선택되었는지 유효성을 검사합니다.
        if surgery == "선택하세요":
            st.error("⚠️ 수술명을 선택해야 합니다.")
            st.session_state['profile_setup_completed'] = False
        else:
            # 선택된 정보를 session_state에 저장합니다.
            st.session_state['profile_setup_completed'] = True
            st.session_state['user_profile'] = {
                "surgery": surgery
            }
            
            # 다음 페이지로 이동하기 위해 상태를 변경하고 새로고침합니다.
            st.session_state.current_page = "necessity"
            st.rerun()