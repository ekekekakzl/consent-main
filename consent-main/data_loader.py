import streamlit as st
import pandas as pd
import os

@st.cache_resource
def load_excel_data(file_path: str):
    if not os.path.exists(file_path):
        st.error(f"🚨 오류: 엑셀 파일을 찾을 수 없습니다! 경로를 확인해주세요: {file_path}")
        return None
    try:
        df_dict = pd.read_excel(file_path, header=None, sheet_name=None)
        return df_dict
    except Exception as e:
        st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

def get_cell_contents_from_dataframe(excel_data_dict: dict, sheet_name: str, cell_ranges: list[str]):
    combined_content_parts = []
    if excel_data_dict is None or sheet_name not in excel_data_dict:
        st.error(f"시트 '{sheet_name}'를 엑셀 데이터에서 찾을 수 없습니다. 설정된 시트 이름과 엑셀 파일 내부 시트 이름을 확인해주세요.")
        return []

    df = excel_data_dict[sheet_name]

    for cell_range in cell_ranges:
        col_letter = ''.join(filter(str.isalpha, cell_range)).upper()
        row_num = int(''.join(filter(str.isdigit, cell_range)))

        col_idx = 0
        for char in col_letter:
            col_idx = col_idx * 26 + (ord(char) - ord('A') + 1)
        col_idx -= 1

        row_idx = row_num - 1

        if row_idx < df.shape[0] and col_idx < df.shape[1]:
            content = df.iloc[row_idx, col_idx]
            if pd.isna(content):
                combined_content_parts.append("")
            else:
                combined_content_parts.append(str(content))
        else:
            combined_content_parts.append("")
    return combined_content_parts