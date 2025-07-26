import streamlit as st
from config import SECTIONS_SIDEBAR_MAP, SECTIONS_ORDER_KEYS

def render_profile_setup():
    with st.form("profile_form"):
        # 이름 입력 필드
        name = st.text_input("이름 *", value=st.session_state.user_profile.get('name', ''))
        
        # 성별 선택 필드
        gender_options = ["선택하세요", "남성", "여성", "기타"]
        current_gender_value = st.session_state.user_profile.get('gender')
        if current_gender_value in gender_options:
            current_gender_index = gender_options.index(current_gender_value)
        else:
            current_gender_index = 0
        gender = st.selectbox("성별 *", gender_options, index=current_gender_index)

        # 연령 입력 필드
        age = st.number_input("연령 *", min_value=0, max_value=120, step=1, format="%d", value=st.session_state.user_profile.get('age', 0))
        
        diagnosis_options = ["선택하세요", "자궁경부암", "난소암", "자궁내막암", "자궁근종"]
        current_diagnosis_value = st.session_state.user_profile.get('diagnosis')
        if current_diagnosis_value in diagnosis_options:
            current_diagnosis_index = diagnosis_options.index(current_diagnosis_value)
        else:
            current_diagnosis_index = 0

        diagnosis = st.selectbox("진단명 *", diagnosis_options, index=current_diagnosis_index)
        
        all_surgery_options = ["선택하세요", "로봇 자궁절제술", "로봇 난소절제술", "로봇 근종절제술", "기타"]
        display_surgery_options = ["선택하세요", "로봇 자궁절제술", "로봇 난소절제술", "로봇 근종절제술", "기타"]
        
        current_surgery_value = st.session_state.user_profile.get('surgery', "선택하세요")
        if current_surgery_value in all_surgery_options:
            current_surgery_index = all_surgery_options.index(current_surgery_value)
        else:
            current_surgery_index = 0

        surgery = st.selectbox("수술명 *", display_surgery_options, index=current_surgery_index)
        
        # 이해 수준 선택 필드 (중복 제거 및 위치 조정)
        education_options = ["선택하세요", "초등학교 졸업", "중학교 졸업", "고등학교 졸업", "대학교 졸업", "대학교 이상"] # 일반인/전문가 수준 추가
        current_education_value = st.session_state.user_profile.get('education_level')
        if current_education_value in education_options:
            current_education_index = education_options.index(current_education_value)
        else:
            current_education_index = 0
        education_level = st.selectbox("학력 *", education_options, index=current_education_index)
        
        # 과거력 및 특이체질/알레르기 통합 필드
        history_and_allergy = st.text_area("과거력 및 특이체질/알레르기", placeholder="과거 수술력, 기존 질환, 현재 복용 중인 약물, 알레르기 등을 입력하세요", value=st.session_state.user_profile.get('history_and_allergy', '')) 

        submitted = st.form_submit_button("다음 단계 >")
    
    if submitted:
        # 필수 입력 필드 검사 강화
        if not name or age <= 0 or gender == "선택하세요" or diagnosis == "선택하세요" or surgery == "선택하세요" or education_level == "선택하세요":
            st.error("⚠️ 이름, 연령, 성별, 진단명, 수술명, 이해 수준은 필수로 입력해야 합니다.")
            st.session_state['profile_setup_completed'] = False
        else:
            st.session_state['profile_setup_completed'] = True
            st.session_state['user_profile'] = {
                "name": name,
                "gender": gender,
                "age": age,
                "diagnosis": diagnosis,
                "surgery": surgery,
                "history_and_allergy": history_and_allergy, # 통합된 필드 이름 사용
                "education_level": education_level
            }
            st.session_state.current_page = "necessity"
            st.rerun()