import streamlit as st

from services import logic

def show_search_console():

  st.set_page_config(page_title="Job Search App", layout="wide")

  st.title('Scout Automation')

  pdfs = st.file_uploader('候補者PDFアップロード', type=['pdf'], accept_multiple_files=True)

  condition1 = st.text_area('一つでも合致しない場合「NG判定」となる条件', placeholder='一つでも合致しない場合「NG判定」となる条件を入力してください、入力内容がそのままプロンプトに反映されるので、箇条書きが好ましいです', height='content')


  condition2 = st.text_area('一つでも当てはまる場合「NG判定」となる条件', placeholder='一つでも当てはまる場合「NG判定」となる検索条件を入力してください、入力内容がそのままプロンプトに反映されるので、箇条書きが好ましいです', height='content')

  if st.button('開始'):
    with st.spinner('処理中です.....'):
      spreadsheet_url = logic.main(condition1, condition2, pdfs)
      st.write(f"作成したシート：{spreadsheet_url}")
