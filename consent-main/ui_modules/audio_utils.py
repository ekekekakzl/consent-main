import streamlit as st 
import edge_tts 
import asyncio 
import re 
import textwrap 

def run_async(coro): 
# ... existing code ...
    return loop.run_until_complete(coro) 

async def _synthesize_with_edge_tts_async(text: str, voice: str, file_name: str, rate: str = "-8%"): 
# ... existing code ...
    await communicate.save(file_name) 

def _clean_text_for_speech(text: str) -> str: 
# ... existing code ...
    return text 

def play_text_as_audio_callback(text_to_speak: str, output_filename: str, voice: str = "ko-KR-SunHiNeural"): 
    """ 
    정제된 텍스트를 edge-tts로 음성 변환하고 재생 상태를 설정하는 콜백 함수. 
    """ 
    try: 
        cleaned_text = _clean_text_for_speech(text_to_speak) 

        # [수정] 텍스트가 비어있거나, 유의미한 문자(글자/숫자)가 없는지 확인합니다.
        # 이렇게 하면 ". , ." 처럼 문장 부호만 남은 텍스트가 API로 전송되는 것을 방지합니다.
        if not cleaned_text or not re.search(r'[가-힣a-zA-Z0-9]', cleaned_text): 
            st.warning("음성으로 변환할 텍스트가 없습니다. (공백, 문장 부호 등만 포함)") 
            return 

        run_async(_synthesize_with_edge_tts_async(cleaned_text, voice, output_filename)) 
        
        st.session_state.audio_file_to_play = output_filename 
        
    except Exception as e: 
        st.error(f"음성 생성에 실패했습니다: {e}") 
        st.session_state.audio_file_to_play = None
