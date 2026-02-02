import streamlit as st
import tempfile
import os
from services.jd import logic

def show_jd_create_console():
  tab1, tab2 = st.tabs(["求人票作成", "会社・事業説明"])

  with tab1:
    company_info = st.text_area('会社情報', placeholder='会社情報を入力してください')

    video_link = st.text_input('録画リンクを入力')

    jd_pdf = st.file_uploader(
      '求人票PDFアップロード',
      type=['pdf'],
      accept_multiple_files=False,
    )

    temperature = st.number_input('temperature_cp', min_value = 0.0, max_value = 2.10, value = 0.5, step = 0.1)

    if st.button('開始'):
      with st.spinner('処理中です.....'):
        # 入力チェック：どちらか欠けている場合は処理しない
        if jd_pdf is None:
          st.error("求人票PDFをアップロードしてください。")
          return

        temp_file_info = [] # [(一時パス, オリジナルファイル名), ...] を格納
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
          tmp_file.write(jd_pdf.getvalue()) # アップロードされたファイルの内容を書き込む
          temp_file_info.append((tmp_file.name, jd_pdf.name))
          print(f"ファイル書き込み完了 ファイルパス: {tmp_file.name}")

        try:
          res = logic.create_jd(company_info, video_link, temp_file_info, temperature)
          st.header("作成した募集要項")
          st.subheader("募集背景", divider=True)
          st.code(res['background'], language=None)
          st.subheader("募集職種", divider=True)
          st.code(res['job_category'], language=None)
          st.subheader("仕事内容", divider=True)
          st.code(res['job_content'], language=None)
          st.subheader("必須要件", divider=True)
          st.code(res['required_requirement'], language=None)
          st.subheader("歓迎要件", divider=True)
          st.code(res['welcome_requirement'], language=None)
          st.subheader("求める人物像", divider=True)
          st.code(res['character_statue'], language=None)
        finally:
          # 4. ローカルの一時ファイルを削除
          for tmp_pdf_path, _ in temp_file_info:
            try:
              os.remove(tmp_pdf_path)
            except FileNotFoundError:
              # 何らかの理由で既に削除されている場合はスキップ
              pass

  with tab2:
    company_info2 = st.text_area('会社情報2', placeholder='会社情報を入力してください')

    temperature_jd = st.number_input('temperature_jd', min_value = 0.0, max_value = 2.10, value = 0.5, step = 0.1)

    if st.button('開始'):
      with st.spinner('処理中です.....'):
        # 入力チェック：どちらか欠けている場合は処理しない
        if company_info2 is None:
          st.error("会社情報を入力してください。")
          return

        try:
          res_company_info = logic.create_business_description(company_info2, temperature_jd)
          st.header("作成した会社・事業説明")
          st.subheader("会社名", divider=True)
          st.code(res_company_info['company_name'], language=None)
          st.subheader("事業サービス名", divider=True)
          st.code(res_company_info['business_service_name'], language=None)
          st.subheader("企業理念", divider=True)
          st.code(res_company_info['company_philosophy'], language=None)
          st.subheader("事業紹介", divider=True)
          st.code(res_company_info['business_introduction'], language=None)
          st.subheader("事業の詳細", divider=True)
          st.code(res_company_info['business_detail'], language=None)
        except Exception as e:
          st.write(f"エラーが発生しました。{e}")

def uploade_file(pdfs):
  file_info = [] # [(一時パス, オリジナルファイル名), ...] を格納
  for uploaded_file in pdfs:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
      tmp_file.write(uploaded_file.getvalue()) # アップロードされたファイルの内容を書き込む
      file_info.append((tmp_file.name, uploaded_file.name))
      print(f"ファイル書き込み完了 ファイルパス: {tmp_file.name}")
  
  return file_info
