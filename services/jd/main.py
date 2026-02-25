import streamlit as st
from services.jd import logic
from utils import upload_files, cleanup_temp_files, inject_code_block_style, show_code_sections

def show_jd_create_console():
  tab1, tab2= st.tabs(["求人票作成", "会社・事業説明"])

  with tab1:
    company_info = st.text_area('会社情報', placeholder='会社情報を入力してください')

    hearing_info = st.text_area('ヒアリング内容', placeholder='ヒアリング内容を入力してください')

    jd_pdfs = st.file_uploader(
      '参考求人票PDFアップロード',
      type=['pdf'],
      accept_multiple_files=True,
    )

    temperature = st.number_input('temperature_cp', min_value = 0.0, max_value = 2.10, value = 0.5, step = 0.1)

    inject_code_block_style()

    if st.button('開始'):
      with st.spinner('処理中です.....'):
        # 入力チェック：どちらか欠けている場合は処理しない
        if jd_pdfs is None:
          st.error("参考求人票PDFをアップロードしてください。")
          return

        temp_file_info = upload_files(jd_pdfs)

        try:
          res = logic.create_jd(company_info, hearing_info, temp_file_info, temperature)
          show_code_sections(
            {
              "募集背景": res["background"],
              "募集職種": res["job_category"],
              "仕事内容": res["job_content"],
              "必須要件": res["required_requirement"],
              "歓迎要件": res["welcome_requirement"],
              "求める人物像": res["character_statue"],
            },
            main_title="作成した募集要項",
          )
        finally:
          cleanup_temp_files(temp_file_info)

  with tab2:
    company_info2 = st.text_area('会社情報2', placeholder='会社情報を入力してください')

    temperature_jd = st.number_input('temperature_jd', min_value = 0.0, max_value = 2.10, value = 0.5, step = 0.1)

    inject_code_block_style()

    if st.button('作成開始(Gemini)'):
      with st.spinner('処理中です.....'):
        # 入力チェック：どちらか欠けている場合は処理しない
        if company_info2 is None:
          st.error("会社情報を入力してください。")
          return

        try:
          res_company_info = logic.create_business_description(company_info2, temperature_jd)
          show_code_sections(
            {
              "会社名": res_company_info["company_name"],
              "事業サービス名": res_company_info["business_service_name"],
              "企業理念": res_company_info["company_philosophy"],
              "事業紹介": res_company_info["business_introduction"],
              "事業の詳細": res_company_info["business_detail"],
            },
            main_title="作成した会社・事業説明",
          )
        except Exception as e:
          st.write(f"エラーが発生しました。{e}")
