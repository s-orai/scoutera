import streamlit as st
import tempfile
import os
from services import logic

def show_search_console():

  st.set_page_config(page_title="Scout Automation", layout="wide")

  st.title('Scout Automation')

  pdfs = st.file_uploader('候補者PDFアップロード', type=['pdf'], accept_multiple_files=True)

  job_pdf = st.file_uploader('求人票アップロード', type=['pdf'], accept_multiple_files=False)

  judge_condition = st.text_area('A/B/C判定の基準', placeholder='判定の基準を入力してください、入力内容がそのままプロンプトに反映されるので、箇条書きが好ましいです', height='content')


  required_condition = st.text_area('必須要件', placeholder='必須要件を入力してください、入力内容がそのままプロンプトに反映されるので、箇条書きが好ましいです', height='content')

  welcome_condition = st.text_area('歓迎要件', placeholder='歓迎要件を入力してください、入力内容がそのままプロンプトに反映されるので、箇条書きが好ましいです', height='content')

  temperature = st.number_input('temperature', min_value = 0.0, max_value = 2.10, value = 0.5, step = 0.1, width=300)


  if st.button('開始'):
    with st.spinner('処理中です.....'):
      # 入力チェック：どちらか欠けている場合は処理しない
      if not pdfs or job_pdf is None:
        st.error("候補者PDFと求人票PDFの両方をアップロードしてください。")
        return

      temp_file_info = [] # [(一時パス, オリジナルファイル名), ...] を格納
      for uploaded_file in pdfs:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
          tmp_file.write(uploaded_file.getvalue()) # アップロードされたファイルの内容を書き込む
          temp_file_info.append((tmp_file.name, uploaded_file.name))
          print(f"ファイル書き込み完了 ファイルパス: {tmp_file.name}")

      temp_job_file_info = [] # [(一時パス, オリジナルファイル名), ...] を格納
      with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_job_file:
        tmp_job_file.write(job_pdf.getvalue()) # アップロードされたファイルの内容を書き込む
        temp_job_file_info.append((tmp_job_file.name, job_pdf.name))
        print(f"ファイル書き込み完了 ファイルパス: {tmp_job_file.name}")

      try:
        # 3. 解析関数の実行
        spreadsheet_url = logic.main(judge_condition, required_condition, welcome_condition, temp_file_info, temp_job_file_info, temperature)
        st.write(f"作成したシート：{spreadsheet_url}")
      finally:
        # 4. ローカルの一時ファイルを削除
        for tmp_pdf_path, _ in temp_file_info:
          try:
            os.remove(tmp_pdf_path)
          except FileNotFoundError:
            # 何らかの理由で既に削除されている場合はスキップ
            pass

        for tmp_job_pdf_path, _ in temp_job_file_info:
          try:
            os.remove(tmp_job_pdf_path)
          except FileNotFoundError:
            pass

