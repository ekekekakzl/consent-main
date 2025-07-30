import streamlit as st

def render_final_summary_page():
    """
    최종 동의서 요약 페이지를 렌더링합니다.
    이 페이지는 모든 동의서 설명을 완료한 후 전체 내용을 요약하여 보여줍니다.
    """
    st.markdown("<h1 class='summary-title'>전체 동의서 요약 📝</h1>", unsafe_allow_html=True)
    st.info("여기에 전체 동의서의 주요 내용이 요약되어 표시될 예정입니다.")

    # TODO: 실제 요약 내용을 생성하고 표시하는 로직을 추가해야 합니다.
    # 예: st.session_state.user_profile을 기반으로 Gemini API를 호출하여 요약 생성
    # 또는 각 섹션의 핵심 내용을 조합하여 표시

    st.markdown("---")

    # 요약 내용이 들어갈 자리 (예시)
    st.markdown("""
    ### 환자 맞춤 요약 (예시)

    환자분께서는 **[진단명]**으로 인해 **[수술명]** 로봇수술을 받으실 예정입니다.

    **주요 내용:**
    * **수술 필요성:** [AI가 생성한 필요성 요약]
    * **수술 방법:** [AI가 생성한 수술 방법 요약]
    * **고려 사항:** [AI가 생성한 고려 사항 요약]
    * **합병증과 관리:** [AI가 생성한 합병증과 관리 요약]
    * **주의 사항:** [AI가 생성한 주의 사항 요약]
    * **자기 결정권:** [AI가 생성한 자기 결정권 요약]

    더 자세한 내용은 각 섹션을 다시 확인하시거나, 의료진에게 문의해주세요.
    """, unsafe_allow_html=True)

    st.markdown("---")
    col_back_to_main, col_re_enter_profile = st.columns(2)
    with col_back_to_main:
        if st.button("메인 페이지로 돌아가기", key="back_to_main_from_summary", use_container_width=True):
            st.session_state.current_page = "main"
            # 필요한 세션 상태 초기화
            st.session_state.chat_history = []
            st.session_state.current_gemini_explanation = ""
            st.session_state.last_loaded_section_key = None
            st.session_state.show_quiz = False
            st.session_state.current_quiz_idx = 0
            st.session_state.current_faq_answer = ""
            st.rerun()
    with col_re_enter_profile:
        if st.button("환자 정보 다시 입력하기", key="re_enter_profile_from_summary", use_container_width=True):
            st.session_state.profile_setup_completed = False
            st.session_state.current_page = "profile_setup"
            st.session_state.user_profile = {}
            st.session_state.chat_history = []
            st.session_state.quiz_answers = {}
            st.session_state.current_section = 0
            st.session_state.current_gemini_explanation = ""
            st.session_state.last_loaded_section_key = None
            st.session_state.show_quiz = False
            st.session_state.current_quiz_idx = 0
            st.session_state.current_faq_answer = ""
            st.rerun()