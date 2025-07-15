import streamlit as st
from data_loader import get_cell_contents_from_dataframe
from gemini_utils import get_gemini_chat_response, get_gemini_response_from_combined_content
from config import SECTION_CELL_MAP, QUIZ_DATA, FAQ_DATA, SECTIONS_SIDEBAR_MAP, SECTIONS_ORDER_KEYS

def clear_user_question_input(key):
    st.session_state[key] = ""

def render_section_page(section_idx, title, description, section_key):
    st.session_state.current_section = section_idx

    st.markdown(f"""
    <div id="section-top-{section_key}" style='display:flex; align-items:center; font-size:1.5rem; font-weight:bold; margin-bottom:8px; gap:8px;'>
        <span>📄</span> {title}
    </div>
    <div style='color:#666; font-size:1rem; margin-bottom:24px;'>
        {description}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <script>
            var element = document.getElementById("section-top-{section_key}");
            if (element) {{
                setTimeout(function() {{
                    element.scrollIntoView({{ behavior: 'instant', block: 'start' }});
                }}, 50);
            }}
        </script>
        """,
        unsafe_allow_html=True
    )

    user_diagnosis = st.session_state.user_profile.get('diagnosis')
    
    if st.session_state.excel_data_dict is None:
        st.error(f"⚠️ 엑셀 동의서 파일을 로드하는 데 실패했습니다. 파일 경로와 형식을 확인해주세요.")
        return

    if not (user_diagnosis and user_diagnosis in SECTION_CELL_MAP[section_key]):
        st.warning(f"선택된 진단명 '{user_diagnosis}'에 대한 '{title}' 정보가 엑셀 파일 매핑에 없습니다. 프로필을 다시 설정하거나 관리자에게 문의해주세요.")
        st.info("메인 페이지로 돌아가 프로필을 다시 설정하거나 관리자에게 문의해주세요.")
        if st.button("프로필 재설정", key="reset_profile_missing_diagnosis_footer"):
            st.session_state.profile_setup_completed = False
            st.session_state.current_page = "profile_setup"
            st.rerun()
        return

    sheet_info = SECTION_CELL_MAP[section_key][user_diagnosis]
    
    combined_content_parts = get_cell_contents_from_dataframe(
        st.session_state.excel_data_dict, sheet_info["sheet"], sheet_info["ranges"]
    )
    
    if combined_content_parts is None:
        st.session_state.current_gemini_explanation = "이 섹션에 대한 설명 내용을 찾을 수 없습니다 (엑셀 파일 문제). 관리자에게 문의해주세요."
        st.warning(f"로드된 엑셀 파일의 시트 '{sheet_info['sheet']}'에서 내용을 가져올 수 없습니다. 시트와 셀 주소를 확인해주세요.")
    else:
        combined_content = " ".join(part for part in combined_content_parts if part)
        
        if not combined_content.strip():
            st.session_state.current_gemini_explanation = "이 섹션에 대한 설명 내용을 찾을 수 없습니다 (엑셀 내용 없음). 엑셀 파일을 확인해주세요."
            st.warning(f"선택된 진단명 '{user_diagnosis}'에 대한 '{title}' 내용이 엑셀 파일의 지정된 셀 ({sheet_info['ranges']})에 없거나 비어있습니다.")
        else:
            if not st.session_state.current_gemini_explanation or \
               st.session_state.get('last_loaded_section_key') != section_key:
                
                # 섹션별 채팅 기록 초기화는 이제 최종 채팅 페이지에서 관리됩니다.
                # st.session_state.chat_history = []
                st.session_state.current_quiz_idx = 0
                st.session_state.show_quiz = False

                with st.spinner(f"AI가 {user_diagnosis}에 대한 {title}을(를) 설명하고 있습니다..."):
                    gemini_explanation = get_gemini_response_from_combined_content(
                        combined_content, 
                        st.session_state.user_profile,
                        current_section_title=title
                    )
                    if not gemini_explanation.strip() or "죄송합니다. AI 모델이 응답하는 데 문제가 발생했습니다." in gemini_explanation:
                        st.session_state.current_gemini_explanation = "AI 설명을 생성하는 데 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
                    else:
                        st.session_state.current_gemini_explanation = gemini_explanation
                
                st.session_state.last_loaded_section_key = section_key
                

    st.markdown(f"<div style='background-color:#f9f9f9; padding:20px; border-radius:10px; border:1px solid #eee;'>{st.session_state.current_gemini_explanation}</div>", unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("💡 이해도 확인 OX 퀴즈")
    
    if section_key in QUIZ_DATA:
        section_quizzes = QUIZ_DATA[section_key]
        
        if st.session_state.current_quiz_idx < len(section_quizzes):
            current_quiz = section_quizzes[st.session_state.current_quiz_idx]
            st.write(f"**문제:** {st.session_state.current_quiz_idx + 1}번. {current_quiz['question']}")
            
            quiz_answer_key = f"quiz_answer_{section_key}_{st.session_state.current_quiz_idx}"
            if quiz_answer_key not in st.session_state.quiz_answers:
                st.session_state.quiz_answers[quiz_answer_key] = None

            col_o, col_x = st.columns(2)
            with col_o:
                if st.button("O", key=f"quiz_O_{section_key}_{st.session_state.current_quiz_idx}", use_container_width=True):
                    st.session_state.quiz_answers[quiz_answer_key] = "O"
                    st.rerun()
                    
            with col_x:
                if st.button("X", key=f"quiz_X_{section_key}_{st.session_state.current_quiz_idx}", use_container_width=True):
                    st.session_state.quiz_answers[quiz_answer_key] = "X"
                    st.rerun()
                    
            if st.session_state.quiz_answers[quiz_answer_key] is not None:
                if st.session_state.quiz_answers[quiz_answer_key] == current_quiz['answer']:
                    st.success(f"정답입니다! 🎉 {current_quiz['explanation']}")
                else:
                    st.error(f"아쉽지만 틀렸어요. 😥 정답은 {current_quiz['answer']}입니다. {current_quiz['explanation']}")
                
                if st.session_state.current_quiz_idx < len(section_quizzes) - 1:
                    if st.button("다음 문제 풀기", key=f"next_quiz_button_{section_key}_{st.session_state.current_quiz_idx}"):
                        st.session_state.current_quiz_idx += 1
                        st.rerun()
                else:
                    st.info("이 섹션의 모든 퀴즈를 완료했습니다! �")
                    if st.button("계속 진행하기", key=f"finish_quiz_button_{section_key}"):
                        st.session_state.show_quiz = False
                        st.session_state.current_quiz_idx = 0
                        st.rerun()
                
        else:
            st.info("이 섹션의 모든 퀴즈를 이미 완료하셨습니다! 다음 단계로 넘어가거나 다른 섹션을 살펴보세요. 😊")
            st.session_state.show_quiz = False
            st.session_state.current_quiz_idx = 0
            
    else:
        st.info("이 섹션에 대한 퀴즈가 아직 준비되지 않았습니다.")

    st.markdown("---")
    st.subheader("🤔 자주 묻는 질문 (FAQ)")
    
    if 'current_faq_answer' not in st.session_state:
        st.session_state.current_faq_answer = ""

    if section_key in FAQ_DATA:
        for i, faq_item in enumerate(FAQ_DATA[section_key]):
            if st.button(faq_item["question"], key=f"faq_q_{section_key}_{i}"):
                st.session_state.current_faq_answer = faq_item["answer"]
                st.rerun()
    else:
        st.info("이 섹션에 대한 자주 묻는 질문이 아직 준비되지 않았습니다.")

    if st.session_state.current_faq_answer:
        st.markdown(f"<div style='background-color:#e6f7ff; padding:15px; border-radius:8px; border:1px solid #91d5ff; margin-top:15px;'><strong>답변:</strong> {st.session_state.current_faq_answer}</div>", unsafe_allow_html=True)
        if st.button("답변 닫기", key=f"clear_faq_answer_{section_key}"):
            st.session_state.current_faq_answer = ""
            st.rerun()

    st.markdown("---")

    current_page_key_index = -1
    for i, key in enumerate(SECTIONS_ORDER_KEYS):
        if SECTIONS_SIDEBAR_MAP[key]["idx"] == section_idx:
            current_page_key_index = i
            break

    cols = st.columns(2)
    with cols[0]:
        if current_page_key_index > 0:
            if st.button("이전 단계", key=f"prev_section_{section_idx}", use_container_width=True):
                st.session_state.current_section = SECTIONS_SIDEBAR_MAP[SECTIONS_ORDER_KEYS[current_page_key_index - 1]]["idx"]
                st.session_state.current_page = SECTIONS_ORDER_KEYS[current_page_key_index - 1]
                st.session_state.show_quiz = False
                st.session_state.current_quiz_idx = 0
                st.session_state.current_gemini_explanation = ""
                st.session_state.last_loaded_section_key = None
                # FAQ 답변 상태 초기화
                st.session_state.current_faq_answer = ""
                st.rerun()
        else:
            if st.button("환자 정보로 돌아가기", key=f"back_to_profile_{section_idx}", use_container_width=True):
                st.session_state.current_page = "profile_setup"
                st.session_state.current_section = 1
                st.session_state.show_quiz = False
                st.session_state.current_quiz_idx = 0
                st.session_state.current_gemini_explanation = ""
                st.session_state.last_loaded_section_key = None
                # FAQ 답변 상태 초기화
                st.session_state.current_faq_answer = ""
                st.rerun()


    with cols[1]:
        if current_page_key_index < len(SECTIONS_ORDER_KEYS) - 1:
            if st.button("다음 단계", key=f"next_section_{section_idx}", use_container_width=True):
                st.session_state.current_section = SECTIONS_SIDEBAR_MAP[SECTIONS_ORDER_KEYS[current_page_key_index + 1]]["idx"]
                st.session_state.current_page = SECTIONS_ORDER_KEYS[current_page_key_index + 1]
                st.session_state.show_quiz = False
                st.session_state.current_quiz_idx = 0
                st.session_state.current_gemini_explanation = ""
                st.session_state.last_loaded_section_key = None
                # FAQ 답변 상태 초기화
                st.session_state.current_faq_answer = ""
                st.rerun()
        elif current_page_key_index == len(SECTIONS_ORDER_KEYS) - 1:
            if st.button("설명 완료", key=f"finish_sections", use_container_width=True):
                st.success("모든 동의서 설명 섹션을 완료했습니다! 이제 궁금한 점이 있다면 아래 채팅창에 물어보세요.")
                st.session_state.current_page = "final_chat" # 최종 채팅 페이지로 이동
                st.session_state.show_quiz = False
                st.session_state.current_quiz_idx = 0
                st.session_state.current_gemini_explanation = ""
                st.session_state.last_loaded_section_key = None
                # FAQ 답변 상태 초기화
                st.session_state.current_faq_answer = ""
                st.rerun()


def render_necessity_page():
    render_section_page(1, "수술 필요성", "로봇수술이 필요한 이유와 중요성에 대해 설명해 드립니다.", "necessity")

def render_method_page():
    render_section_page(2, "수술 방법", "로봇을 이용한 수술 절차와 과정에 대해 설명해 드립니다.", "method")

def render_considerations_page():
    render_section_page(3, "고려 사항", "수술 전후 고려해야 할 주요 사항에 대해 설명해 드립니다.", "considerations")

def render_side_effects_page():
    render_section_page(4, "부작용", "로봇수술로 발생할 수 있는 잠재적 부작용에 대해 설명해 드립니다.", "side_effects")

def render_precautions_page():
    render_section_page(5, "주의사항", "수술 전후 환자분이 꼭 지켜야 할 주의사항에 대해 설명해 드립니다.", "precautions")

def render_self_determination_page():
    render_section_page(6, "자기결정권", "환자분의 자기 결정권과 관련된 중요한 내용에 대해 설명해 드립니다.", "self_determination")