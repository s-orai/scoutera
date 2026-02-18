import streamlit as st
import tempfile
import os
from services.screening import logic

def show_screening_console():

  candidate_info = st.text_area('候補者情報', placeholder='候補者情報を入力してください')

  candidate_pdfs = st.file_uploader(
    '候補者PDFアップロード',
    type=['pdf'],
    accept_multiple_files=True,
  )

  jd_pdf = st.file_uploader(
    '求人票PDFアップロード',
    type=['pdf'],
    accept_multiple_files=False,
  )

  required_condition = st.text_area('必須要件', placeholder='必須要件を入力してください、入力内容がそのままプロンプトに反映されるので、箇条書きが好ましいです')

  welcome_condition = st.text_area('歓迎要件', placeholder='歓迎要件を入力してください、入力内容がそのままプロンプトに反映されるので、箇条書きが好ましいです')

  st.markdown(
    """
    <style>
    pre code {
        white-space: pre-wrap !important;
        word-break: break-word !important;
    }
    </style>
    """,
    unsafe_allow_html=True
  )

  if st.button('開始'):
    with st.spinner('処理中です.....'):
      # 入力チェック：candidate_pdfsとcandidate_infoどちらも入力されていない場合は処理しない
      if not candidate_pdfs and not candidate_info:
        st.error("候補者PDFまたは候補者情報のいずれかを入力してください。")
        return

      temp_file_info = [] # [(一時パス, オリジナルファイル名), ...] を格納
      for uploaded_file in candidate_pdfs:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
          tmp_file.write(uploaded_file.getvalue()) # アップロードされたファイルの内容を書き込む
          temp_file_info.append((tmp_file.name, uploaded_file.name))
          print(f"ファイル書き込み完了 ファイルパス: {tmp_file.name}")

      temp_job_file_info = [] # [(一時パス, オリジナルファイル名), ...] を格納
      with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_job_file:
        tmp_job_file.write(jd_pdf.getvalue()) # アップロードされたファイルの内容を書き込む
        temp_job_file_info.append((tmp_job_file.name, jd_pdf.name))
        print(f"ファイル書き込み完了 ファイルパス: {tmp_job_file.name}")
      try:
        result = logic.screening(candidate_info, required_condition, welcome_condition, temp_file_info, temp_job_file_info)
        st.header("書類選考結果")
        st.subheader("評価理由", divider=True)
        st.code(result['evaluation_reason'], language=None)
        st.subheader("必須要件", divider=True)
        st.code(result['required_condition'], language=None)
        st.subheader("歓迎要件", divider=True)
        st.code(result['welcome_condition'], language=None)
        st.subheader("評価結果", divider=True)
        st.code(result['evaluation_result'], language=None)
      except Exception as e:
        st.write(f"エラーが発生しました。{e}")

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