import streamlit as st
from services.screening import logic
from utils import upload_files, cleanup_temp_files

def show_screening_console():

  candidate_info = st.text_area('候補者情報', placeholder='候補者情報を入力してください')

  candidate_pdfs = st.file_uploader(
    '候補者PDFアップロード_スクリーニング',
    type=['pdf'],
    accept_multiple_files=True,
  )

  jd_pdf = st.file_uploader(
    '求人票PDFアップロード_スクリーニング',
    type=['pdf'],
    accept_multiple_files=False,
  )

  required_condition = st.text_area('必須要件_スクリーニング', placeholder='必須要件を入力してください、入力内容がそのままプロンプトに反映されるので、箇条書きが好ましいです')

  welcome_condition = st.text_area('歓迎要件_スクリーニング', placeholder='歓迎要件を入力してください、入力内容がそのままプロンプトに反映されるので、箇条書きが好ましいです')

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
      
      if not jd_pdf:
        st.error("求人票PDFをアップロードしてください。")
        return

      temp_file_info = []
      if candidate_pdfs:
        temp_file_info = upload_files(candidate_pdfs)

      temp_job_file_info = upload_files(jd_pdf)
      
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
        if candidate_pdfs:
          cleanup_temp_files(temp_file_info)
        cleanup_temp_files(temp_job_file_info)