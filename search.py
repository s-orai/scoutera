import streamlit as st
import tempfile
import os
from services import logic

def show_search_console():

  st.set_page_config(page_title="Scout Automation", layout="wide")

  st.title('Scout Automation')

  pdfs = st.file_uploader('候補者PDFアップロード', type=['pdf'], accept_multiple_files=True)

  condition1 = st.text_area('A/B/C判定の基準', placeholder='判定の基準を入力してください、入力内容がそのままプロンプトに反映されるので、箇条書きが好ましいです', height='content')


  condition2 = st.text_area('必須要件', placeholder='必須要件を入力してください、入力内容がそのままプロンプトに反映されるので、箇条書きが好ましいです', height='content')

  condition3 = st.text_area('歓迎要件', placeholder='歓迎要件を入力してください、入力内容がそのままプロンプトに反映されるので、箇条書きが好ましいです', height='content')


  if st.button('開始'):
    with st.spinner('処理中です.....'):
      temp_file_info = [] # [(一時パス, オリジナルファイル名), ...] を格納
      for uploaded_file in pdfs:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
          tmp_file.write(uploaded_file.getvalue()) # アップロードされたファイルの内容を書き込む
          temp_file_info.append((tmp_file.name, uploaded_file.name))

      try:
        # 3. 解析関数の実行
        spreadsheet_url = logic.main_by_gemini(condition1, condition2, condition3, temp_file_info)
        st.write(f"作成したシート：{spreadsheet_url}")
      finally:
        # 4. ローカルの一時ファイルを削除
        for tmp_pdf_path, _ in temp_file_info:
          os.remove(tmp_pdf_path)

  # if st.button('OpenAIで開始'):
  #   with st.spinner('処理中です.....'):
  #     spreadsheet_url = logic.main(condition1, condition2, condition3, pdfs)
  #     st.write(f"作成したシート：{spreadsheet_url}")
