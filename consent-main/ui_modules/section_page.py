import streamlit as st
import os
import base64
import re
from config import QUIZ_DATA, FAQ_DATA, SECTIONS_SIDEBAR_MAP, SECTIONS_ORDER_KEYS
from gemini_utils import get_gemini_response_from_combined_content, synthesize_speech

def _play_text_as_audio_callback(text_to_speak):
    """
    텍스트를 음성으로 변환하여 재생하는 콜백 함수.
    """
    cleaned_text = re.sub(r'[^\w\s.,?!가-힣a-zA-Z0-9]', ' ', text_to_speak)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    if not cleaned_text:
        return

    audio_bytes = synthesize_speech(cleaned_text)
    if audio_bytes:
        base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
        audio_html = f"""
        <audio controls autoplay style="width: 100%;">
            <source src="data:audio/mp3;base64,{base64_audio}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        st.session_state.current_audio_html = audio_html
    else:
        st.error("음성 생성에 실패했습니다. 인터넷 연결을 확인하거나 잠시 후 다시 시도해주세요.")
        st.session_state.current_audio_html = ""

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
                if st.button("환자 정보로 돌아가기", key=f"back_to_profile_{section_idx}", use_container_width=True):
                    st.session_state.profile_setup_completed = False
                    st.session_state.current_page = "profile_setup"
                    st.rerun()

        with nav_cols[1]:
            if current_page_key_index < len(SECTIONS_ORDER_KEYS) - 1:
                if st.button("다음 단계", key=f"next_section_{section_idx}", use_container_width=True):
                    st.session_state.current_page = SECTIONS_ORDER_KEYS[current_page_key_index + 1]
                    st.rerun()
            else:
                if st.button("설명 완료", key=f"finish_sections", use_container_width=True):
                    st.session_state.current_page = "final_chat"
                    st.rerun()

def render_section_page(section_idx, title, description, section_key):
    """
    각 동의서 섹션 페이지를 렌더링하는 핵심 함수.
    """
    # 페이지가 변경되면 관련 세션 상태 초기화
    if st.session_state.get('last_loaded_section_key') != section_key:
        st.session_state.current_gemini_explanation = ""
        st.session_state.current_quiz_idx = 0
        st.session_state.quiz_answers = {}
        st.session_state.current_faq_answer = ""
        st.session_state.current_audio_html = ""

    # 설명 내용 가져오기
    if not st.session_state.current_gemini_explanation:
        explanation = get_gemini_response_from_combined_content(
            user_profile=st.session_state.user_profile,
            current_section_title=title
        )
        st.session_state.current_gemini_explanation = explanation
        st.session_state.last_loaded_section_key = section_key

    # --- 메인 설명 영역 (왼쪽) ---
    col_left, col_right = st.columns([0.6, 0.4], gap="large")
    with col_left:
        title_col, play_col = st.columns([0.7, 0.3])
        with title_col:
            st.markdown(f"### {title}")
            st.caption(description)
        with play_col:
            if st.session_state.current_gemini_explanation:
                st.button("음성 재생 ▶️", key=f"play_section_explanation_{section_key}", use_container_width=True,
                          on_click=_play_text_as_audio_callback, args=(st.session_state.current_gemini_explanation,))

        if section_key == "method":
            img_path = os.path.join(os.path.dirname(__file__), "../images/로봇수술이미지.png")
            if os.path.exists(img_path):
                st.image(img_path, caption="[로봇수술 시스템 구성 요소 이미지]", use_container_width=True)

        explanation_text = st.session_state.get('current_gemini_explanation', '')
        if explanation_text:
            paragraphs = re.split(r'\n\s*\n', explanation_text.strip())
            for paragraph in paragraphs:
                if paragraph.strip():
                    st.markdown(paragraph, unsafe_allow_html=True)

    # --- 상호작용 영역 (오른쪽) ---
    with col_right:
        # --- 퀴즈 섹션 ---
        st.subheader("💡 이해도 확인 OX 퀴즈")
        section_quizzes = QUIZ_DATA.get(section_key, [])

        if section_quizzes:
            if 'current_quiz_idx' not in st.session_state:
                st.session_state.current_quiz_idx = 0

            if st.session_state.current_quiz_idx < len(section_quizzes):
                current_quiz = section_quizzes[st.session_state.current_quiz_idx]
                st.write(f"**문제 {st.session_state.current_quiz_idx + 1}번.** {current_quiz['question']}")

                quiz_answer_key = f"quiz_answer_{section_key}_{st.session_state.current_quiz_idx}"

                cols = st.columns(2)
                if cols[0].button("O", key=f"quiz_O_{quiz_answer_key}", use_container_width=True):
                    st.session_state.quiz_answers[quiz_answer_key] = "O"
                    st.rerun()
                if cols[1].button("X", key=f"quiz_X_{quiz_answer_key}", use_container_width=True):
                    st.session_state.quiz_answers[quiz_answer_key] = "X"
                    st.rerun()

                if quiz_answer_key in st.session_state.quiz_answers:
                    user_answer = st.session_state.quiz_answers[quiz_answer_key]
                    if user_answer == current_quiz['answer']:
                        st.success(f"정답입니다! 🎉 {current_quiz['explanation']}")
                    else:
                        st.error(f"아쉽지만 틀렸어요. 😥 정답은 {current_quiz['answer']}입니다. {current_quiz['explanation']}")

                    if st.session_state.current_quiz_idx < len(section_quizzes) - 1:
                        if st.button("다음 문제 풀기", key=f"next_quiz_{quiz_answer_key}"):
                            st.session_state.current_quiz_idx += 1
                            st.rerun()
                    else:
                        st.info("이 섹션의 모든 퀴즈를 완료했습니다! 🎉")
            else:
                st.info("이 섹션의 모든 퀴즈를 완료했습니다! 🎉")
        else:
            st.info("이 섹션에 대한 퀴즈가 아직 준비되지 않았습니다.")

        # --- FAQ 섹션 ---
        st.subheader("🤔 자주 묻는 질문 (FAQ)")
        section_faqs = FAQ_DATA.get(section_key, [])

        if section_faqs:
            for i, faq_item in enumerate(section_faqs):
                if st.button(faq_item["question"], key=f"faq_q_{section_key}_{i}"):
                    st.session_state.current_faq_answer = faq_item["answer"]
        else:
            st.info("이 섹션에 대한 자주 묻는 질문이 아직 준비되지 않았습니다.")

        if st.session_state.current_faq_answer:
            st.markdown(f"<div class='faq-answer-box'><strong>답변:</strong> {st.session_state.current_faq_answer}</div>", unsafe_allow_html=True)
            st.button("음성 재생 ▶️", key=f"play_faq_answer_{section_key}", use_container_width=True,
                      on_click=_play_text_as_audio_callback, args=(st.session_state.current_faq_answer,))
            if st.button("답변 닫기", key=f"clear_faq_answer_{section_key}"):
                st.session_state.current_faq_answer = ""
                st.rerun()

        # --- 네비게이션 버튼 ---
        render_section_navigation_buttons(section_idx, col_right)


def render_necessity_page():
    render_section_page(1, "수술 필요성", "로봇수술이 필요한 이유와 중요성에 대해 설명해 드립니다.", "necessity")

def render_method_page():
    render_section_page(2, "수술 방법", "로봇을 이용한 수술 절차와 과정에 대해 설명해 드립니다.", "method")

def render_considerations_page():
    render_section_page(3, "고려 사항", "수술 전후 고려해야 할 주요 사항에 대해 설명해 드립니다.", "considerations")

def render_side_effects_page():
    render_section_page(4, "합병증과 관리", "로봇수술로 발생할 수 있는 잠재적 합병증과 관리방법에 대해 설명해 드립니다.", "side_effects")

def render_precautions_page():
    render_section_page(5, "주의사항", "수술 전후 환자분이 꼭 지켜야 할 주의사항에 대해 설명해 드립니다.", "precautions")

def render_self_determination_page():
    render_section_page(6, "자기결정권", "환자분의 자기 결정권과 관련된 중요한 내용에 대해 설명해 드립니다.", "self_determination")