import streamlit as st
import asyncio
import edge_tts
import re
import os
import tempfile
from typing import Optional

# 1. 텍스트 정리 함수: TTS 전용 텍스트 추출 및 불필요한 HTML/마크다운 태그 제거
def extract_tts_text(html_content: str) -> str:
    """
    HTML 마크업이 포함된 설명 내용에서 TTS용 텍스트를 추출하고 정리합니다.
    - 'tts-only' span 태그 내용이 있으면 그것을 최우선으로 사용합니다.
    - 'TTS-SKIP' 주석 사이의 내용은 제거합니다.
    - 그 외 나머지 일반적인 HTML 태그(br, mark, strong 등)는 제거합니다.
    """
    # 1. TTS-ONLY 텍스트 추출 (최우선)
    # <span class="tts-only">...</span> 패턴 검색
    tts_only_match = re.search(r'<span class="tts-only">(.*?)<\/span>', html_content, re.DOTALL)
    if tts_only_match:
        # TTS-only 내용에서 불필요한 공백과 줄바꿈 제거 후 반환
        tts_text = tts_only_match.group(1).strip()
        # TTS-only 텍스트 내의 HTML 태그는 제거 (혹시 모를 상황 대비)
        return re.sub(r'<[^>]+>', '', tts_text)

    # 2. TTS-SKIP 영역 제거
    # <!-- TTS-SKIP-START -->...<!-- TTS-SKIP-END --> 사이의 내용을 제거
    cleaned_content = re.sub(r'<!--\s*TTS-SKIP-START\s*-->.*?<!--\s*TTS-SKIP-END\s*-->', '', html_content, flags=re.DOTALL)
    
    # 3. 그 외 일반적인 HTML/마크다운 태그 제거 (마크다운은 대부분 스트림릿 렌더링 시 제거되지만, HTML 태그를 확실히 제거)
    # 모든 HTML 태그(예: <br>, <mark>, <strong>, <table> 등) 제거
    tts_text = re.sub(r'<[^>]+>', '', cleaned_content)
    
    # 4. 여러 개의 공백/줄바꿈을 하나로 줄이기
    tts_text = re.sub(r'\s+', ' ', tts_text).strip()
    
    return tts_text

# 2. 오디오 파일 생성 (비동기 함수를 동기적으로 호출)
def generate_audio_file(text: str, file_path: str) -> bool:
    """
    Edge-TTS를 사용하여 텍스트를 오디오 파일로 변환합니다.
    성공 시 True, 실패 시 False를 반환합니다.
    """
    # 한국어 남성 음성 선택 (발음이 정확하고 듣기 편한 음성)
    KOREAN_VOICE = "ko-KR-BokHyeomNeural"
    
    # edge_tts가 비동기 함수이므로, Streamlit 환경에서 동기적으로 실행
    async def _generate():
        try:
            communicate = edge_tts.Communicate(text, KOREAN_VOICE)
            await communicate.save(file_path)
            return True
        except Exception as e:
            st.error(f"오디오 생성 중 오류가 발생했습니다: {e}")
            return False

    # asyncio.run을 사용하여 비동기 함수를 실행하고 결과 반환
    return asyncio.run(_generate())

# 3. 오디오 재생 버튼 및 로직
def play_audio_button(raw_html_content: str, key: str):
    """
    오디오 재생 버튼을 렌더링하고, 클릭 시 오디오를 생성하여 재생합니다.
    key는 Streamlit 위젯을 구분하기 위해 섹션별로 고유해야 합니다.
    """
    # 1. TTS용 텍스트 추출
    tts_text = extract_tts_text(raw_html_content)
    
    if not tts_text:
        st.info("재생할 오디오 텍스트가 없습니다.")
        return

    # 세션 상태에 오디오 파일 경로 및 생성 상태 저장
    audio_file_path_key = f'audio_file_path_{key}'
    audio_generated_key = f'audio_generated_{key}'

    if audio_file_path_key not in st.session_state:
        st.session_state[audio_file_path_key] = None
    if audio_generated_key not in st.session_state:
        st.session_state[audio_generated_key] = False

    # 2. 오디오 생성/재생 버튼
    if st.button("🔊 설명 듣기", key=key):
        # 로딩 스피너 표시
        with st.spinner("오디오를 생성 중입니다... 잠시만 기다려주세요."):
            
            # 기존 오디오 파일이 있으면 삭제 (재생 버튼이 여러 번 눌릴 경우 및 재실행 시 파일 정리)
            if st.session_state[audio_file_path_key]:
                try:
                    os.remove(st.session_state[audio_file_path_key])
                except OSError as e:
                    # 파일이 이미 없거나 권한 문제 등으로 삭제에 실패할 수 있음 (경고만 표시)
                    st.warning(f"기존 오디오 파일 삭제 실패: {e}")
            
            # 임시 파일 생성
            # delete=False로 설정하여 Streamlit이 파일을 사용하는 동안 삭제되지 않도록 보호
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            temp_file_path = temp_file.name
            temp_file.close()
            
            # 오디오 생성 시도
            if generate_audio_file(tts_text, temp_file_path):
                st.session_state[audio_file_path_key] = temp_file_path
                st.session_state[audio_generated_key] = True
                st.toast("오디오 생성이 완료되었습니다!", icon="✅")
            else:
                # 실패 시 상태 초기화 및 오류 메시지는 generate_audio_file에서 처리
                st.session_state[audio_file_path_key] = None
                st.session_state[audio_generated_key] = False

    # 3. 오디오 생성 완료 후 재생 위젯 표시
    if st.session_state[audio_generated_key] and st.session_state[audio_file_path_key]:
        audio_file_path = st.session_state[audio_file_path_key]
        
        try:
            with open(audio_file_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                # 오디오 컨트롤러 표시
                st.audio(audio_bytes, format='audio/mp3', start_time=0)
        except FileNotFoundError:
            st.error("오디오 파일을 찾을 수 없습니다. 다시 생성해 주세요.")
