import streamlit as st
import edge_tts
import asyncio
import re
import textwrap
import os # [❗️수정] 1. os 모듈을 임포트합니다.

def run_async(coro):
    """Streamlit과 같은 동기 환경에서 비동기 코드를 실행하기 위한 헬퍼 함수."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

async def _synthesize_with_edge_tts_async(text: str, voice: str, file_name: str, rate: str = "-8%"):
    """
    edge-tts를 사용하여 음성 파일을 비동기적으로 생성합니다.
    rate의 기본값을 -8%로 설정하여 약간 느리게 말하도록 합니다.
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(file_name)

def _clean_text_for_speech(text: str) -> str:
    """
    [❗️수정됨] 음성 합성을 위해 텍스트를 정리합니다.
    HTML에서 'tts-only' 클래스 스팬과 'TTS-ONLY:' 주석의 내용만 추출합니다.
    """
    text = textwrap.dedent(text)
    
    # 1. 'TTS-ONLY:' 주석에서 텍스트 추출
    tts_only_comment_pattern = re.compile(r'<!--\s*TTS-ONLY:\s*(.*?)\s*-->', re.DOTALL)
    comment_texts = tts_only_comment_pattern.findall(text)
    
    # 2. 'tts-only' 클래스 스팬에서 텍스트 추출
    tts_only_span_pattern = re.compile(r'<span[^>]+class\s*=\s*["\'“”]tts-only["\'“”][^>]*>(.*?)</span>', re.DOTALL | re.IGNORECASE)
    span_texts = tts_only_span_pattern.findall(text)
    
    # 3. 추출된 모든 텍스트 결합
    all_tts_texts = comment_texts + span_texts
    
    if not all_tts_texts:
        return "" # 말할 내용이 없음
        
    combined_text = ' '.join(all_tts_texts)
    
    # 4. 결합된 텍스트에서 나머지 HTML 태그 (예: <br>) 및 공백 정리
    # tts-only 스팬 안에 <br> 태그 등이 포함되어 있을 수 있으므로, 여기서 한 번 더 정리합니다.
    cleaned_text = re.sub(r'<[^>]+>', ' ', combined_text) # HTML 태그 제거
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip() # 공백 정리
    
    # 5. 기존의 복잡한 정제 로직(개행 변환, 마크다운 제거 등)은
    #    문서 전체를 대상으로 하므로 버그를 유발. tts-only 텍스트만 처리하도록 단순화.
    
    return cleaned_text

def play_text_as_audio_callback(text_to_speak: str, output_filename: str, voice: str = "ko-KR-SunHiNeural"):
    """
    [❗️수정] 텍스트를 음성 변환하고, st.session_state 대신 파일 경로를 반환합니다.
    """
    try:
        cleaned_text = _clean_text_for_speech(text_to_speak)

        if not cleaned_text:
            st.warning("음성으로 변환할 텍스트가 없습니다.")
            return None  # [❗️수정] 실패 시 None 반환

        run_async(_synthesize_with_edge_tts_async(cleaned_text, voice, output_filename))
        
        # [❗️추가] 2. 파일이 디스크에 실제로 생성되었는지 확인합니다.
        if not os.path.exists(output_filename):
            st.error("오디오 파일 생성 후 디스크에서 파일을 찾을 수 없습니다.")
            return None
        
        # [❗️수정] st.session_state 설정 대신, 성공 시 파일 이름 반환
        return output_filename
        
    except Exception as e:
        st.error(f"음성 생성에 실패했습니다: {e}")
        # [❗️수정] st.session_state 설정 대신, 실패 시 None 반환
        return None
