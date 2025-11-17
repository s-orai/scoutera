import streamlit as st
import ai_matching
import pandas as pd
from clients import google_client


# スプレッドシートへエクスポート
def export_to_spredsheet(df):
    client = google_client.GoogleClient()

    # 1. 新しいスプレッドシートを作成（共有ドライブのフォルダ内）
    spreadsheet_id = client.create_spreadsheet()

    # 2. データを書き込み
    spreadsheet_url = client.write_data(spreadsheet_id, df)

    return spreadsheet_url



def main(condition1, condition2, pdfs):
  json = ai_matching.create_list(pdfs, condition1, condition2)
  df = pd.DataFrame(json['result'])
  # df = df.rename(columns={
  #   "judge": "判定",
  #   "reason": "判定理由",
  #   "message": "スカウト文"
  # })

  return export_to_spredsheet(df)




