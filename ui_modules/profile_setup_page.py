import streamlit as st

def render_profile_setup():
    """
    사용자로부터 '성별'과 '수술명'만 입력받는 페이지를 렌더링합니다.
    """
    # st.form을 사용하여 입력 항목을 그룹화하고, 제출 버튼을 누를 때 한 번에 처리합니다.
    with st.form("profile_form"):
        
        # 2개의 열을 만들어 성별과 수술명 선택란을 나란히 배치합니다.
        col1, col2 = st.columns(2)

        with col1:
            # 성별 선택을 위한 selectbox 위젯
            gender_options = ["선택하세요", "남성", "여성"]
            
            # 이전에 입력한 값이 있으면 그 값을 기본값으로 설정합니다.
            current_gender_value = st.session_state.user_profile.get('gender', "선택하세요")
            current_gender_index = gender_options.index(current_gender_value) if current_gender_value in gender_options else 0

            gender = st.selectbox(
                label="성별 *",
                options=gender_options,
                index=current_gender_index
            )

        with col2:
            # 수술명 선택을 위한 selectbox 위젯
            surgery_options = ["선택하세요", "로봇보조 자궁절제술", "로봇보조 전립선절제술"]
            
            # 이전에 입력한 값이 있으면 그 값을 기본값으로 설정합니다.
            current_surgery_value = st.session_state.user_profile.get('surgery', "선택하세요")
            current_surgery_index = surgery_options.index(current_surgery_value) if current_surgery_value in surgery_options else 0

            surgery = st.selectbox(
                label="수술명 *",
                options=surgery_options,
                index=current_surgery_index
            )
        
        # 폼 제출 버튼
        submitted = st.form_submit_button("설명 듣기 시작 >")
    
    # "설명 듣기 시작 >" 버튼이 클릭되었을 때 실행될 로직
    if submitted:
        # 성별과 수술명이 모두 선택되었는지 유효성을 검사합니다.
        if gender == "선택하세요" or surgery == "선택하세요":
            st.error("⚠️ 성별과 수술명을 모두 선택해야 합니다.")
            st.session_state['profile_setup_completed'] = False
        else:
            # 선택된 정보를 session_state에 저장합니다.
            st.session_state['profile_setup_completed'] = True
            st.session_state['user_profile'] = {
                "gender": gender,
                "surgery": surgery
            }
            
            # 다음 페이지로 이동하기 위해 상태를 변경하고 새로고침합니다.
            st.session_state.current_page = "necessity"
            st.rerun()