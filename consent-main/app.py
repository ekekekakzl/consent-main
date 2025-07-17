import streamlit as st
import os
import json # session_state를 위한 import 유지

# 분리된 모듈에서 필요한 함수와 상수를 임포트
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

# --- 페이지 설정 ---
st.set_page_config(layout="wide")

# --- 커스텀 CSS 로드 및 적용 ---
css_file_path = os.path.join(os.path.dirname(__file__), "style", "styles.css")
if os.path.exists(css_file_path):
    with open(css_file_path, 'r', encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning(f"CSS 파일을 찾을 수 없습니다: {css_file_path}. 기본 스타일이 적용됩니다.")

# --- 1. Streamlit Secrets에서 설정 변수 로드 및 Gemini API 설정 ---
CONFIG_LOADED = False
try:
    GEMINI_API_KEY = st.secrets["gemini_api_key"]
    if configure_gemini(GEMINI_API_KEY):
        CONFIG_LOADED = True
except KeyError as e:
    st.error(f"⚠️ 설정 오류: Streamlit Secrets에서 '{e}' 키를 찾을 수 없습니다. `secrets.toml` 파일을 확인해주세요.")
except Exception as e:
    st.error(f"⚠️ 설정 오류: {e}")


# --- 2. 세션 상태 초기화 ---
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


# --- 엑셀 파일은 앱 시작 시 한 번만 로드하여 세션 상태에 저장 ---
if 'excel_data_dict' not in st.session_state:
    st.session_state.excel_data_dict = load_excel_data(EXCEL_FILE_PATH)


# 최종 채팅 페이지 함수
def render_final_chat_page():
    # st.title("궁금한 점을 물어보세요! 💬") 대신 커스텀 마크다운 사용
    st.markdown("<h1 class='final-chat-title'>궁금한 점을 물어보세요! 💬</h1>", unsafe_allow_html=True)
    st.info("모든 동의서 설명을 완료했습니다. 궁금한 점이 있다면 무엇이든 물어보세요.")

    # 채팅 기록 표시
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # st.chat_input 대신 st.text_input과 st.button 사용
    user_query = st.text_input("궁금한 점을 입력하세요:", key="final_chat_text_input")
    send_button = st.button("전송", key="final_chat_send_button")

    if send_button and user_query: # 버튼 클릭 및 입력 내용이 있을 때
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        with st.spinner("답변 생성 중..."):
            try:
                response_text = get_gemini_chat_response(
                    st.session_state.chat_history[:-1],
                    user_query,
                    initial_explanation="환자분께서 동의서 내용을 모두 이해하셨습니다. 이제 추가 질문에 답변해주세요."
                )
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"Gemini API 호출 중 오류 발생: {e}")
                st.session_state.chat_history.append({"role": "assistant", "content": "죄송합니다. 답변을 생성하는 데 문제가 발생했습니다."})
        
        # 새로운 메시지 추가 후 맨 아래로 스크롤 (이 페이지에서만)
        st.markdown(
            """
            <script>
                setTimeout(function() {
                    window.scrollTo({ top: document.body.scrollHeight, behavior: "instant" });
                }, 100);
            </script>
            """,
            unsafe_allow_html=True
        )
        st.rerun() # 입력 필드 초기화 및 변경 사항 반영
    
    st.markdown("---")
    if st.button("메인 페이지로 돌아가기", key="back_to_main_from_final_chat"):
        st.session_state.current_page = "main"
        st.session_state.chat_history = [] # 최종 채팅 기록 초기화
        st.rerun()


# --- Main App Logic ---
def main():
    # --- 페이지 렌더링 시 맨 위로 스크롤하는 강력한 JavaScript 코드 ---
    # 이 코드는 앱이 다시 렌더링될 때마다 실행되어 스크롤 위치를 맨 위로 강제합니다.
    # 가능한 모든 스크롤 가능한 요소를 대상으로 시도하여 안정성을 극대화합니다.
    st.markdown(
        """
        <script>
            function forceScrollToTopAggressively() {
                // 1. window (최상위 브라우저 창) 스크롤
                window.scrollTo({ top: 0, behavior: 'instant' });
                
                // 2. document.body 및 document.documentElement (HTML 요소) 스크롤
                document.body.scrollTop = 0; // For Safari
                document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera

                // 3. Streamlit의 메인 앱 뷰 컨테이너 스크롤
                const appViewContainer = document.querySelector('[data-testid="stAppViewContainer"]');
                if (appViewContainer) {
                    appViewContainer.scrollTop = 0;
                }

                // 4. Streamlit의 'main' 요소 스크롤 (주요 콘텐츠 영역)
                const mainElement = document.querySelector('main');
                if (mainElement) {
                    mainElement.scrollTop = 0;
                }
            }
            
            // 페이지 로드 및 업데이트 시 단일 호출로 안정성 확보
            // Streamlit의 렌더링 완료를 기다리기 위해 충분한 지연 시간을 줍니다.
            setTimeout(forceScrollToTopAggressively, 200); /* 200ms 지연 후 스크롤 시도 */
            setTimeout(forceScrollToTopAggressively, 500); /* 추가적인 안전 장치 */
        </script>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state["logged_in"]:
        render_login_page()
        return

    # 사이드바 제목 (st.sidebar.title 대신 커스텀 마크다운 사용)
    st.sidebar.markdown("<h2 class='sidebar-menu-title'>메뉴</h2>", unsafe_allow_html=True)
    
    if st.sidebar.button("👤 환자 정보 입력", key="profile_input_button"):
        st.session_state.current_page = "profile_setup"
        st.session_state.current_section = 1
        st.session_state.current_gemini_explanation = ""
        st.session_state.last_loaded_section_key = None
        st.rerun()
        

    if st.session_state.profile_setup_completed:
        st.sidebar.markdown("---")
        st.sidebar.subheader("진행 단계")
        # 사이드바에 진행 단계 네비게이션 추가
        step_names = ["환자정보", "수술필요성", "수술방법", "고려사항", "부작용", "주의사항", "자기결정권"]
        for i, step_name in enumerate(step_names):
            # 네비게이션을 위한 페이지 키 결정
            if i == 0:
                page_key = "profile_setup"
            else:
                page_key = SECTIONS_ORDER_KEYS[i-1] # SECTIONS_ORDER_KEYS는 0번 인덱스부터 시작

            # 현재 활성화된 단계인지 확인하여 텍스트를 굵게 표시
            is_active_step = False
            if st.session_state.current_page == page_key:
                if page_key == "profile_setup" and st.session_state.get('current_step', 1) == 1:
                    is_active_step = True
                # 현재 섹션 인덱스와 단계 인덱스가 일치하는지 확인
                elif page_key != "profile_setup" and st.session_state.current_section == (i + 1):
                    is_active_step = True

            display_text = f"{i+1}. {step_name}"
            if is_active_step:
                display_text = f"**{i+1}. {step_name}**" # 활성화된 단계는 굵게 표시

            if st.sidebar.button(
                display_text,
                key=f"sidebar_step_nav_{i}",
                help=f"'{step_name}' 단계로 이동합니다.",
                on_click=lambda idx=i, pk=page_key: (
                    setattr(st.session_state, 'current_step', idx + 1),
                    setattr(st.session_state, 'current_page', pk),
                    setattr(st.session_state, 'show_quiz', False),
                    setattr(st.session_state, 'current_quiz_idx', 0),
                    setattr(st.session_state, 'current_gemini_explanation', ""), # 섹션 변경 시 설명 초기화
                    setattr(st.session_state, 'last_loaded_section_key', None), # 마지막 로드 섹션 키 초기화
                    setattr(st.session_state, 'current_faq_answer', "") # FAQ 답변 초기화
                )
            ):
                st.rerun()
    else:
        st.sidebar.info("환자 정보 입력이 완료되면 동의서 설명 항목이 활성화됩니다.")

    st.sidebar.markdown("---") # 진행 단계와 다음 메뉴 사이 구분선

    # '로그아웃' 버튼
    if st.sidebar.button("로그아웃", key="logout_button_sidebar"):
        st.session_state["logged_in"] = False
        st.session_state.clear()
        st.rerun()

    if st.session_state.excel_data_dict is None:
        st.title("🚨 오류: 엑셀 파일 로드 실패 🚨")
        st.error("애플리케이션을 시작하는 데 필요한 엑셀 동의서 파일을 찾거나 읽을 수 없습니다.")
        st.info(f"'{EXCEL_FILE_PATH}' 경로에 파일이 올바르게 위치해 있는지 확인하고, 파일 형식이 올바른지 확인해주세요.")
        return

    # 페이지 라우팅
    if st.session_state.current_page == "profile_setup":
        render_profile_setup()
    elif st.session_state.profile_setup_completed and st.session_state.current_page in SECTIONS_SIDEBAR_MAP:
        # 각 섹션 페이지 함수를 매핑하여 호출
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
        # 메인 페이지 제목 (st.title 대신 커스텀 마크다운 사용)
        st.markdown("<h1 class='main-app-title'>환자 맞춤형 로봇수술 동의서 설명 도우미 🤖</h1>", unsafe_allow_html=True)
        st.markdown("""
        이 애플리케이션은 환자분의 프로필 정보와 **미리 로드된 동의서 엑셀 파일**을 기반으로,
        Gemini AI가 각 섹션의 내용을 이해하기 쉽고 따뜻하게 설명해 드립니다.
        <br><br>
        **시작하려면 환자 정보를 입력해주세요.**
        """, unsafe_allow_html=True)
        
        if not st.session_state.profile_setup_completed:
            st.markdown("---")
            st.subheader("환자 정보 입력하기")
            st.session_state.current_page = "profile_setup"
            st.session_state.current_section = 1
            render_profile_setup()
        else:
            st.success("✅ 동의서 엑셀 파일이 성공적으로 로드되었고, 환자 정보가 입력되었습니다! 이제 왼쪽 메뉴에서 설명할 항목을 선택해주세요.")

if __name__ == "__main__":
    main()