import streamlit as st
import os
from config import QUIZ_DATA, FAQ_DATA, SECTIONS_ORDER_KEYS
from gemini_utils import get_gemini_response_from_combined_content
# 새로 만든 오디오 유틸리티 파일에서 콜백 함수를 가져옵니다.
from ui_modules.audio_utils import play_text_as_audio_callback

def render_section_navigation_buttons(section_idx, parent_column):
    """
    섹션 간 이동을 위한 '이전 단계' 및 '다음 단계' 버튼을 렌더링합니다.
    """
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
    """
    각 동의서 섹션 페이지를 렌더링하는 핵심 함수.
    """
    if st.session_state.get('last_loaded_section_key') != section_key:
        st.session_state.current_gemini_explanation = ""
        st.session_state.quiz_answers = {}
        st.session_state.current_faq_answer = ""
        st.session_state.audio_file_to_play = None

    if not st.session_state.current_gemini_explanation:
        explanation = get_gemini_response_from_combined_content(
            user_profile=st.session_state.user_profile,
            current_section_title=title
        )
        st.session_state.current_gemini_explanation = explanation
        st.session_state.last_loaded_section_key = section_key

    col_left, col_right = st.columns([0.7, 0.3], gap="large")
    with col_left:
        title_col, play_col = st.columns([0.7, 0.3])
        with title_col:
            st.markdown(f"### {title}")
            st.caption(description)
        with play_col:
            if st.session_state.current_gemini_explanation:
                # on_click에서 audio_utils의 함수를 호출하고, 고유한 파일 이름을 전달합니다.
                st.button("음성 재생 ▶️", key=f"play_section_explanation_{section_key}", use_container_width=True,
                          on_click=play_text_as_audio_callback, 
                          args=(st.session_state.current_gemini_explanation, "section_audio.mp3"))

        if section_key == "method":
            img_path = os.path.join(os.path.dirname(__file__), "../images/로봇수술이미지.png")
            if os.path.exists(img_path):
                st.image(img_path, caption="[로봇수술 시스템 구성 요소]", use_container_width=True)

        explanation_text = st.session_state.get('current_gemini_explanation', '')
        if explanation_text:
            st.markdown(explanation_text, unsafe_allow_html=True)
        
        if st.session_state.get('audio_file_to_play'):
            st.audio(st.session_state.audio_file_to_play, autoplay=True)

    with col_right:
        st.subheader("💡 이해도 확인 OX 퀴즈")
        section_quizzes = QUIZ_DATA.get(section_key, [])

        if section_quizzes:
            for i, quiz_item in enumerate(section_quizzes):
                quiz_answer_key = f"quiz_answer_{section_key}_{i}"

                st.markdown(f"<div class='quiz-question-box'>문제 {i + 1}. {quiz_item['question']}</div>", unsafe_allow_html=True)

                cols = st.columns(2)
                if cols[0].button("O", key=f"quiz_O_{quiz_answer_key}", use_container_width=True):
                    st.session_state.quiz_answers[quiz_answer_key] = "O"
                    st.rerun()
                if cols[1].button("X", key=f"quiz_X_{quiz_answer_key}", use_container_width=True):
                    st.session_state.quiz_answers[quiz_answer_key] = "X"
                    st.rerun()

                if quiz_answer_key in st.session_state.quiz_answers:
                    user_answer = st.session_state.quiz_answers[quiz_answer_key]
                    if user_answer == quiz_item['answer']:
                        st.success(f"정답입니다! 🎉 {quiz_item['explanation']}")
                    else:
                        st.error(f"아쉽지만 틀렸어요. 😥 정답은 {quiz_item['answer']}입니다. {quiz_item['explanation']}")
        else:
            st.info("이 섹션에 대한 퀴즈가 아직 준비되지 않았습니다.")
        st.markdown("---")

        st.subheader("🤔 자주 묻는 질문 (FAQ)")
        section_faqs = FAQ_DATA.get(section_key, [])

        if section_faqs:
            st.markdown("<div class='secondary-button-wrapper'>", unsafe_allow_html=True)
            for i, faq_item in enumerate(section_faqs):
                if st.button(faq_item["question"], key=f"faq_q_{section_key}_{i}", use_container_width=True):
                    if st.session_state.get('current_faq_answer') == faq_item["answer"]:
                        st.session_state.current_faq_answer = ""
                    else:
                        st.session_state.current_faq_answer = faq_item["answer"]
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("이 섹션에 대한 자주 묻는 질문이 아직 준비되지 않았습니다.")

        if st.session_state.get('current_faq_answer'):
            st.markdown(f"<div class='faq-answer-box'><strong>답변:</strong> {st.session_state.current_faq_answer}</div>", unsafe_allow_html=True)
            if st.button("답변 닫기", key=f"clear_faq_answer_{section_key}"):
                st.session_state.current_faq_answer = ""
                st.rerun()

        st.markdown("---")
        render_section_navigation_buttons(section_idx, col_right)

def render_necessity_page():
    render_section_page(1, "필요성", "로봇수술이 필요한 이유", "necessity")

def render_method_page():
    render_section_page(2, "방법", "로봇 수술에 대한 설명과 수술 과정", "method")

def render_considerations_page():
    render_section_page(3, "고려 사항", "로봇수술 시 고려할 사항", "considerations")

def render_side_effects_page():
    render_section_page(4, "합병증", "로봇수술로 발생할 수 있는 합병증", "side_effects")

def render_precautions_page():
    render_section_page(5, "수술 후 관리", "수술 후 지켜야 할 사항", "precautions")

def render_self_determination_page():

    render_section_page(6, "주의사항과 자기결정권", "동의서 서명 전 알아야 되는 사항", "self_determination")
