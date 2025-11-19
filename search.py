import streamlit as st

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
      spreadsheet_url = logic.main(condition1, condition2, condition3, pdfs)
      st.write(f"作成したシート：{spreadsheet_url}")
