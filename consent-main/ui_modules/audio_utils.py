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
    """ 
    edge-tts를 사용하여 음성 파일을 비동기적으로 생성합니다. 
    rate의 기본값을 -8%로 설정하여 약간 느리게 말하도록 합니다. 
    """ 
    communicate = edge_tts.Communicate(text, voice, rate=rate) 
    await communicate.save(file_name) 

def _clean_text_for_speech(text: str) -> str: 
    """ 
    음성 합성을 위해 텍스트를 정리합니다. HTML, 마크다운, 특수문자 등을 제거하고 자연스러운 쉼을 추가합니다. 
    """ 
    # 텍스트 블록의 공통된 들여쓰기를 제거하여 처리 오류를 방지합니다. 
    text = textwrap.dedent(text) 

    # [개선] 화면에는 보이지만 음성에서는 제외할 텍스트를 안정적인 주석 방식으로 먼저 제거합니다. 
    screen_only_pattern = re.compile(r'<!--\s*TTS-SKIP-START\s*-->.*?<!--\s*TTS-SKIP-END\s*-->', re.DOTALL) 
    text = screen_only_pattern.sub('', text) 

    # 0. 음성용 제목 주석(<!-- TTS-TITLE: ... -->)과 그 아래의 표를 찾아 제거합니다.
    table_pattern = re.compile(r'(?:^\s*<!--\s*TTS-TITLE:\s*(.*?)\s*-->\s*\n+)?((?:^\s*\|(?:.*?\|)+\s*\n)+)', re.MULTILINE) 
    text = table_pattern.sub('', text) 
    
    # [개선] 음성으로만 나올 텍스트를 처리합니다. (두 가지 형식 모두 지원) 
    tts_only_comment_pattern = re.compile(r'<!--\s*TTS-ONLY:\s*(.*?)\s*-->') 
    text = tts_only_comment_pattern.sub(r'\1 ', text) 
    
    tts_only_span_pattern = re.compile(r'<span[^>]+class\s*=\s*["\'“”]tts-only["\'“”][^>]*>(.*?)</span>', re.DOTALL | re.IGNORECASE) 
    text = tts_only_span_pattern.sub(r'\1 ', text) 

    # 1. 이제 나머지 모든 HTML 태그를 제거합니다. 
    text = re.sub(r'<[^>]+>', '', text) 
    
    # 2. 링크 형식 제거 (예: [텍스트](링크)) 
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text) 
    
    # 3. 인라인 코드(`), 볼드(**), 이탤릭(*) 마커 제거 
    text = re.sub(r'[`*_]{1,2}', '', text) 
    
    # 4. 헤딩 마커(#) 제거 
    text = re.sub(r'^\s*#+\s*', '', text, flags=re.MULTILINE) 
    
    # 5. 목록 마커 처리 
    text = re.sub(r'(^\s*\d+)\.\s+', r'\1 ', text, flags=re.MULTILINE) 
    text = re.sub(r'^\s*[\*\-]\s+', '', text, flags=re.MULTILINE) 

    # 6. 자연스러운 쉼 추가 
    text = text.replace('\n\n', '. . . ') 
    text = text.replace('\n', ', ') 

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

        run_async(_synthesize_with_edge_tts_async(cleaned_text, voice, output_filename)) 
        
        st.session_state.audio_file_to_play = output_filename 
        
    except Exception as e: 
        st.error(f"음성 생성에 실패했습니다: {e}") 

        st.session_state.audio_file_to_play = None
