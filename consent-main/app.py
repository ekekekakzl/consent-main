import streamlit as st
import os
import json

from config import (
    EXCEL_FILE_PATH, USERNAME, PASSWORD,
    SECTIONS_SIDEBAR_MAP, SECTIONS_ORDER_KEYS
)
from data_loader import load_excel_data
from gemini_utils import configure_gemini, get_gemini_chat_response
from ui_modules.login_page import render_login_page
from ui_modules.profile_setup_page import render_profile_setup
from ui_modules.section_page import (
    render_necessity_page, render_method_page, render_considerations_page,
    render_side_effects_page, render_precautions_page, render_self_determination_page
)

st.set_page_config(layout="wide")

css_file_path = os.path.join(os.path.dirname(__file__), "style", "styles.css")
if os.path.exists(css_file_path):
    with open(css_file_path, 'r', encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning(f"CSS 파일을 찾을 수 없습니다: {css_file_path}. 기본 스타일이 적용됩니다.")

CONFIG_LOADED = False
try:
    GEMINI_API_KEY = st.secrets["gemini_api_key"]
    if configure_gemini(GEMINI_API_KEY):
        CONFIG_LOADED = True
except KeyError as e:
    st.error(f"⚠️ 설정 오류: Streamlit Secrets에서 '{e}' 키를 찾을 수 없습니다. `secrets.toml` 파일을 확인해주세요.")
except Exception as e:
    st.error(f"⚠️ 설정 오류: {e}")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0
if 'section_scores' not in st.session_state:
    st.session_state.section_scores = {}
if 'profile_setup_completed' not in st.session_state:
    st.session_state.profile_setup_completed = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "main"
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False
if 'all_users_data' not in st.session_state:
    st.session_state.all_users_data = []
if 'user_data' not in st.session_state:
    st.session_state.user_data = []
if 'logged_in' not in st.session_state:
    st.session_state["logged_in"] = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'current_gemini_explanation' not in st.session_state:
    st.session_state.current_gemini_explanation = ""
if 'show_quiz' not in st.session_state:
    st.session_state.show_quiz = False
if 'current_quiz_idx' not in st.session_state:
    st.session_state.current_quiz_idx = 0
if 'profile_page' not in st.session_state:
    st.session_state.profile_page = "profile_input"
if 'last_loaded_section_key' not in st.session_state:
    st.session_state.last_loaded_section_key = None


if 'excel_data_dict' not in st.session_state:
    st.session_state.excel_data_dict = load_excel_data(EXCEL_FILE_PATH)


# 모든 섹션 완료 후 최종 채팅 페이지 렌더링 함수
def render_final_chat_page():
    st.markdown(f'<div id="final-chat-top"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <script>
            var element = document.getElementById("final-chat-top");
            if (element) {{
                setTimeout(function() {{
                    element.scrollIntoView({{ behavior: 'instant', block: 'start' }});
                }}, 50);
            }}
        </script>
        """,
        unsafe_allow_html=True
    )

    st.title("궁금한 점을 물어보세요! �")
    st.info("모든 동의서 설명을 완료했습니다. 궁금한 점이 있다면 무엇이든 물어보세요.")

    # 채팅 기록 표시
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 채팅 입력
    user_query = st.chat_input("궁금한 점을 물어보세요!", key="final_chat_input")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        with st.spinner("답변 생성 중..."):
            try:
                # 최종 채팅에서는 섹션별 초기 설명 대신 전체 컨텍스트를 활용할 수 있도록
                # 현재까지의 모든 대화 기록을 기반으로 응답을 생성합니다.
                # 필요하다면 여기에 전체 엑셀 내용을 요약한 컨텍스트를 추가할 수도 있습니다.
                response_text = get_gemini_chat_response(
                    st.session_state.chat_history[:-1],
                    user_query,
                    initial_explanation="환자분께서 동의서 내용을 모두 이해하셨습니다. 이제 추가 질문에 답변해주세요."
                )
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"Gemini API 호출 중 오류 발생: {e}")
                st.session_state.chat_history.append({"role": "assistant", "content": "죄송합니다. 답변을 생성하는 데 문제가 발생했습니다."})
        
        st.rerun()
    
    st.markdown("---")
    if st.button("메인 페이지로 돌아가기", key="back_to_main_from_final_chat"):
        st.session_state.current_page = "main"
        st.session_state.chat_history = [] # 최종 채팅 기록 초기화
        st.rerun()


def main():
    if not st.session_state["logged_in"]:
        render_login_page()
        return

    st.sidebar.title("메뉴")

    step_names = ["환자정보", "수술필요성", "수술방법", "고려사항", "부작용", "주의사항", "자기결정권"]
    st.sidebar.subheader("진행 단계")
    for i, step_name in enumerate(step_names):
        if i == 0:
            page_key = "profile_setup"
        else:
            page_key = SECTIONS_ORDER_KEYS[i-1]

        is_active_step = False
        if st.session_state.current_page == page_key:
            if page_key == "profile_setup" and st.session_state.get('current_step', 1) == 1:
                is_active_step = True
            elif page_key != "profile_setup" and st.session_state.current_section == (i + 1):
                is_active_step = True

        display_text = f"{i+1}. {step_name}"
        if is_active_step:
            display_text = f"**{i+1}. {step_name}**"

        if st.sidebar.button(
            display_text,
            key=f"sidebar_step_nav_{i}",
            help=f"'{step_name}' 단계로 이동합니다.",
            on_click=lambda idx=i, pk=page_key: (
                setattr(st.session_state, 'current_step', idx + 1),
                setattr(st.session_state, 'current_page', pk),
                setattr(st.session_state, 'show_quiz', False),
                setattr(st.session_state, 'current_quiz_idx', 0),
                setattr(st.session_state, 'current_gemini_explanation', ""),
                setattr(st.session_state, 'last_loaded_section_key', None),
                setattr(st.session_state, 'current_faq_answer', "") # FAQ 답변 상태 초기화
            )
        ):
            st.rerun()

    st.sidebar.markdown("---")

    if st.sidebar.button("로그아웃", key="logout_button_sidebar"):
        st.session_state["logged_in"] = False
        st.session_state.clear()
        st.rerun()

    if st.session_state.excel_data_dict is None:
        st.title("🚨 오류: 엑셀 파일 로드 실패 🚨")
        st.error("애플리케이션을 시작하는 데 필요한 엑셀 동의서 파일을 찾거나 읽을 수 없습니다.")
        st.info(f"'{EXCEL_FILE_PATH}' 경로에 파일이 올바르게 위치해 있는지 확인하고, 파일 형식이 올바른지 확인해주세요.")
        return

    if st.session_state.current_page == "profile_setup":
        render_profile_setup()
    elif st.session_state.profile_setup_completed and st.session_state.current_page in SECTIONS_SIDEBAR_MAP:
        page_functions = {
            "necessity": render_necessity_page,
            "method": render_method_page,
            "considerations": render_considerations_page,
            "side_effects": render_side_effects_page,
            "precautions": render_precautions_page,
            "self_determination": render_self_determination_page,
        }
        page_functions[st.session_state.current_page]()
    elif st.session_state.current_page == "final_chat":
        render_final_chat_page()
    else:
        st.title("환자 맞춤형 로봇수술 동의서 이해쑥쑥 설명 도우미 🤖")
        st.markdown("""
        환자분의 정보와 동의서 내용을 기반으로, AI가 이해하기 쉽고 따뜻하게 설명해 드립니다.
        """, unsafe_allow_html=True)
        
        if not st.session_state.profile_setup_completed:
            st.markdown("---")
            st.subheader("나의 정보를 입력해주세요")
            st.session_state.current_page = "profile_setup"
            st.session_state.current_section = 1
            render_profile_setup()
        else:
            st.success("✅ 동의서에 대한 설명을 들어주셔서 감사합니다. 최선을 다하여 안전하게 수술하도록 하겠습니다.")

if __name__ == "__main__":
    main()