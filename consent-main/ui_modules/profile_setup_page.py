import streamlit as st
from config import SECTIONS_SIDEBAR_MAP, SECTIONS_ORDER_KEYS

def render_profile_setup():
    step_names = ["환자정보", "수술필요성", "수술방법", "고려사항", "부작용", "주의사항", "자기결정권"]
    if 'current_step' not in st.session_state:
        st.session_state['current_step'] = 1

    step = st.session_state['current_step']

    if step == 1:
        with st.form("profile_form"):
            age = st.number_input("연령 *", min_value=0, max_value=120, step=1, format="%d", value=st.session_state.user_profile.get('age', 0))
            
            diagnosis_options = ["선택하세요", "자궁경부암", "난소암", "자궁내막암"]
            current_diagnosis_value = st.session_state.user_profile.get('diagnosis')
            if current_diagnosis_value in diagnosis_options:
                current_diagnosis_index = diagnosis_options.index(current_diagnosis_value)
            else:
                current_diagnosis_index = 0

            diagnosis = st.selectbox("진단명 *", diagnosis_options, index=current_diagnosis_index)
            
            surgery = st.selectbox("수술명 *", ["선택하세요", "로봇 자궁절제술", "로봇 난소절제술"], index=["선택하세요", "로봇 자궁절제술", "로봇 근종절제술", "로봇 난소절제술", "기타"].index(st.session_state.user_profile.get('surgery', "선택하세요")))
            history = st.text_area("과거력", placeholder="과거 수술력, 현재 복용 중인 약물, 기존 질환 등을 입력하세요", value=st.session_state.user_profile.get('history', ''))
            allergy = st.text_area("특이체질 및 알레르기", placeholder="약물 알레르기, 음식 알레르기, 특이체질 등을 입력하세요", value=st.session_state.user_profile.get('allergy', ''))
            submitted = st.form_submit_button("다음 단계 >")
        if submitted:
            if age <= 0 or surgery == "선택하세요":
                st.error("⚠️ 연령, 수술명은 필수로 입력해야 합니다.")
                st.session_state['profile_setup_completed'] = False
            else:
                st.session_state['profile_setup_completed'] = True
                st.session_state['user_profile'] = {
                    "age": age,
                    "diagnosis": diagnosis,
                    "surgery": surgery,
                    "history": history,
                    "allergy": allergy
                }
                st.session_state['current_step'] = 2
                st.session_state.current_page = "necessity"
                st.rerun()
    elif st.session_state.profile_setup_completed:
        pass
    else:
        st.warning("먼저 환자 정보를 입력하고 '다음 단계'를 눌러주세요.")
        st.session_state['current_step'] = 1