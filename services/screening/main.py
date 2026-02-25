import streamlit as st
from services.screening import logic
from utils import upload_files, cleanup_temp_files, inject_code_block_style, show_code_sections

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

  inject_code_block_style()

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
        show_code_sections(
          {
            "評価理由": result["evaluation_reason"],
            "必須要件": result["required_condition"],
            "歓迎要件": result["welcome_condition"],
            "評価結果": result["evaluation_result"],
          },
          main_title="書類選考結果",
        )
      except Exception as e:
        st.write(f"エラーが発生しました。{e}")

      finally:
        if candidate_pdfs:
          cleanup_temp_files(temp_file_info)
        cleanup_temp_files(temp_job_file_info)