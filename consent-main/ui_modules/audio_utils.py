import streamlit as st
import edge_tts
import asyncio
import re
import textwrap

def run_async(coro):
    """Streamlit과 같은 동기 환경에서 비동기 코드를 실행하기 위한 헬퍼 함수."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

async def _synthesize_with_edge_tts_async(text: str, voice: str, file_name: str):
    """edge-tts를 사용하여 음성 파일을 비동기적으로 생성합니다."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_name)

def _clean_text_for_speech(text: str) -> str:
    """
    음성 합성을 위해 텍스트를 정리합니다. HTML, 마크다운, 특수문자 등을 제거하고 자연스러운 쉼을 추가합니다.
    """
    # 텍스트 블록의 공통된 들여쓰기를 제거하여 처리 오류를 방지합니다.
    text = textwrap.dedent(text)

    def process_table_with_context(match):
        """표와 그 제목을 함께 처리하여 자연스러운 음성 안내 문구를 생성하는 내부 함수."""
        # group(1)은 TTS 주석에서 추출한 제목, group(2)는 표 블록입니다.
        title = match.group(1).strip() if match.group(1) else None
        table_text = match.group(2)
        
        lines = table_text.strip().split('\n')
        
        readable_rows = []
        for line in lines:
            # 마크다운 표의 구분선(예: |---|---|)은 건너뜁니다.
            if re.fullmatch(r'[\s|:-]+', line):
                continue
            
            # 각 행을 '|' 기준으로 나누고, 빈 셀은 제외합니다.
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                row_text = ', '.join(cells)
                readable_rows.append(row_text)
        
        readable_table = '. '.join(readable_rows)
        if readable_table:
            if title:
                # 음성용 제목이 있으면 제목과 함께 안내 문구를 생성합니다.
                return f"다음은 '{title}' 표의 내용입니다. {readable_table}."
            else:
                # 제목이 없으면 일반적인 안내 문구를 생성합니다.
                return f"다음은 표의 내용입니다. {readable_table}."
        return ""

    # 0. 음성용 제목 주석(<!-- TTS-TITLE: ... -->)과 그 아래의 표를 찾아 먼저 처리합니다.
    # 이 패턴은 선택적인 TTS-TITLE 주석과 그 바로 뒤에 오는 표 블록을 찾습니다.
    table_pattern = re.compile(r'(?:^\s*<!--\s*TTS-TITLE:\s*(.*?)\s*-->\s*\n+)?((?:^\s*\|(?:.*?\|)+\s*\n)+)', re.MULTILINE)
    text = table_pattern.sub(process_table_with_context, text)
    
    # 1. HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 2. 링크 형식 제거 (예: [텍스트](링크))
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    
    # 3. 인라인 코드(`), 볼드(**), 이탤릭(*) 마커 제거
    text = re.sub(r'[`*_]{1,2}', '', text)
    
    # 4. 헤딩 마커(#) 제거
    text = re.sub(r'^\s*#+\s*', '', text, flags=re.MULTILINE)
    
    # 5. 목록 마커 처리
    # 숫자 목록 (예: 1.) -> 숫자만 남김 (예: 1)
    text = re.sub(r'(^\s*\d+)\.\s+', r'\1 ', text, flags=re.MULTILINE)
    # 불릿 목록 (예: * 또는 -) -> 마커 제거
    text = re.sub(r'^\s*[\*\-]\s+', '', text, flags=re.MULTILINE)

    # 6. 자연스러운 쉼 추가
    text = text.replace('\n\n', '. ').replace('\n', ', ')

    # 7. 기타 불필요한 특수문자 제거
    text = re.sub(r'[^\w\s.,?!가-힣a-zA-Z0-9]', ' ', text)
    
    # 8. 여러 공백을 하나로 축소
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def play_text_as_audio_callback(text_to_speak: str, output_filename: str, voice: str = "ko-KR-SunHiNeural"):
    """
    정제된 텍스트를 edge-tts로 음성 변환하고 재생 상태를 설정하는 콜백 함수.
    """
    try:
        cleaned_text = _clean_text_for_speech(text_to_speak)

        if not cleaned_text:
            st.warning("음성으로 변환할 텍스트가 없습니다.")
            return

        # 비동기 함수를 실행하여 음성 파일을 생성합니다.
        run_async(_synthesize_with_edge_tts_async(cleaned_text, voice, output_filename))
        
        # 세션 상태에 재생할 오디오 파일 경로를 저장합니다.
        st.session_state.audio_file_to_play = output_filename
        
    except Exception as e:
        st.error(f"음성 생성에 실패했습니다: {e}")
        st.session_state.audio_file_to_play = None