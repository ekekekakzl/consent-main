import streamlit as st

def get_gemini_response_from_combined_content(user_profile, current_section_title):
    """
    config.py에서 하드코딩된 기본 설명을 수술명에 따라 가져옵니다.
    """
    from config import HARDCODED_BASE_EXPLANATIONS

    surgery = user_profile.get('surgery', '알 수 없음')
    section_explanations = HARDCODED_BASE_EXPLANATIONS.get(current_section_title, {})
    
    explanation_content = section_explanations.get(surgery, "")

    if isinstance(explanation_content, dict):
        base = section_explanations.get(explanation_content.get("base_explanation"), "")
        additional = explanation_content.get("additional_explanation", "")
        return f"{base}\n\n{additional}"
    elif explanation_content == "_common_explanation":
        return section_explanations.get("_common_explanation", "")
    
    return explanation_content or f"'{surgery}'에 대한 '{current_section_title}' 설명이 준비되지 않았습니다."