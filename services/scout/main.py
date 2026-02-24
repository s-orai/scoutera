import streamlit as st
import os
from services.scout import logic
from utils import upload_files

def show_search_console():
  tab1, tab2, tab3 = st.tabs(["候補者ピックアップ", "プロンプト作成", "スカウト素材出力"])

  with tab1:
    # セッション状態の初期化
    # file_uploaderをリセットするためのカウンターとして使用します
    if "uploader_key" not in st.session_state:
      st.session_state["uploader_key"] = 0

    pdfs = st.file_uploader(
      '候補者PDFアップロード',
      type=['pdf'],
      accept_multiple_files=True,
      key=f"uploader_{st.session_state['uploader_key']}"
    )

    if st.button("すべてのファイルを削除"):
      # キーを更新することで、file_uploaderを初期状態に戻します
      st.session_state["uploader_key"] += 1
      st.rerun()

    job_pdf = st.file_uploader('求人票アップロード', type=['pdf'], accept_multiple_files=False)

    required_condition = st.text_area('必須要件', placeholder='必須要件を入力してください、入力内容がそのままプロンプトに反映されるので、箇条書きが好ましいです')

    welcome_condition = st.text_area('歓迎要件', placeholder='歓迎要件を入力してください、入力内容がそのままプロンプトに反映されるので、箇条書きが好ましいです')


    if st.button('開始'):
      with st.spinner('処理中です.....'):
        # 入力チェック：どちらか欠けている場合は処理しない
        if not pdfs or job_pdf is None:
          st.error("候補者PDFと求人票PDFの両方をアップロードしてください。")
          return

        temp_file_info = upload_files(pdfs)
        temp_job_file_info = upload_files(job_pdf)

        try:
          spreadsheet_url = logic.main(required_condition, welcome_condition, temp_file_info, temp_job_file_info)
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

  with tab2:
    pdfs_A = st.file_uploader('A評価された候補者PDFアップロード', type=['pdf'], accept_multiple_files=True)

    pdfs_B = st.file_uploader('B評価された候補者PDFアップロード', type=['pdf'], accept_multiple_files=True)

    pdfs_C = st.file_uploader('C評価された候補者PDFアップロード', type=['pdf'], accept_multiple_files=True)

    job_pdf = st.file_uploader('求人票PDFアップロード', type=['pdf'], accept_multiple_files=False)

    comment_B = st.text_area('B評価コメント', placeholder='B評価のコメントを入力してください')

    comment_C = st.text_area('C評価コメント', placeholder='C評価のコメントを入力してください')

    if st.button('プロンプト作成開始'):
      with st.spinner('処理中です.....'):
        # 入力チェック：どちらか欠けている場合は処理しない
        if (pdfs_A or pdfs_B or pdfs_C or job_pdf) is None:
          st.error("評価PDF A, B, Cと求人票PDFの全てをアップロードしてください。")
          return

        if not comment_B or comment_C is None:
          st.error("評価コメントを入力してください。")
          return

        pdfs_A_info = upload_files(pdfs_A)
        pdfs_B_info = upload_files(pdfs_B)
        pdfs_C_info = upload_files(pdfs_C)
        job_file_info = upload_files(job_pdf)

        try:
          spreadsheet_url = logic.create_prompt(pdfs_A_info, pdfs_B_info, pdfs_C_info, comment_B, comment_C, job_file_info)
          st.write(f"作成したシート：{spreadsheet_url}")
        finally:
          # 4. ローカルの一時ファイルを削除
          for tmp_pdfA_path, _ in pdfs_A_info:
            try:
              os.remove(tmp_pdfA_path)
            except FileNotFoundError:
              # 何らかの理由で既に削除されている場合はスキップ
              pass

          for tmp_pdfB_path, _ in pdfs_B_info:
            try:
              os.remove(tmp_pdfB_path)
            except FileNotFoundError:
              # 何らかの理由で既に削除されている場合はスキップ
              pass

          for tmp_pdfC_path, _ in pdfs_C_info:
            try:
              os.remove(tmp_pdfC_path)
            except FileNotFoundError:
              # 何らかの理由で既に削除されている場合はスキップ
              pass

          for tmp_job_pdf_path, _ in job_file_info:
            try:
              os.remove(tmp_job_pdf_path)
            except FileNotFoundError:
              # 何らかの理由で既に削除されている場合はスキップ
              pass

  with tab3:
    pdf = st.file_uploader('求人票PDFアップロード_スカウト素材出力', type=['pdf'], accept_multiple_files=False)

    if st.button('スカウト素材出力開始'):
      with st.spinner('処理中です.....'):
        if pdfs is None:
          st.error("スカウト素材PDFをアップロードしてください。")
          return

        job_file_info = upload_files(pdf)

        try:
          spreadsheet_url = logic.create_scout_material(job_file_info)
          st.write(f"作成したシート：{spreadsheet_url}")
        finally:
          # 4. ローカルの一時ファイルを削除
          for job_file_path, _ in job_file_info:
            try:
              os.remove(job_file_path)
            except FileNotFoundError:
              # 何らかの理由で既に削除されている場合はスキップ
              pass
