import ai_matching
import pandas as pd
import create_prompt_logic
from clients import google_client
import streamlit as st

scout_folder_id = st.secrets["google"]["scout_folder_id"]
create_prompt_folder_id = st.secrets["google"]["create_prompt_folder_id"]

# スプレッドシートへエクスポート
def export_to_spredsheet(df, folder_id):
    client = google_client.GoogleClient()

    # 1. 新しいスプレッドシートを作成（共有ドライブのフォルダ内）
    spreadsheet_id = client.create_spreadsheet(folder_id)

    # 2. データを書き込み
    spreadsheet_url = client.write_data(spreadsheet_id, df)

    return spreadsheet_url


def main(judge_condition, required_condition, welcome_condition, pdfs, job_pdf, temperature):
  json = ai_matching.create_list_by_gemini(pdfs, judge_condition, required_condition, welcome_condition, job_pdf, temperature)
  data_dicts = [item.model_dump() for item in json]
  df = pd.DataFrame(data_dicts)
  df.columns = [
    "ID",
    "STEP1における必須要件を満たすか",
    "STEP1における歓迎要件を満たすか",
    "必須要件、歓迎要件の結果を踏まえた候補者の評価理由",
    "STEP1の結果(候補者の評価結果)",
    "STEP2の結果(声がけした背景の文章)"
  ]

  return export_to_spredsheet(df, scout_folder_id)

def create_prompt(pdfs_A, pdfs_B, pdfs_C, comment_B, comment_C, job_pdf, temperature):
  json = create_prompt_logic.create_list_by_gemini(pdfs_A, pdfs_B, pdfs_C, comment_B, comment_C, job_pdf, temperature)

  data_dicts = [json.model_dump()]
  df = pd.DataFrame(data_dicts)
  df.columns = [
    "A評価の候補者が持っている共通のスキル",
    "A,B評価の候補者とC評価の候補者のスキルの差分",
    "A評価の候補者とB評価の候補者のスキルの差分",
    "必須要件（箇条書きで出力）",
    "歓迎要件（箇条書きで出力）"
  ]

  return export_to_spredsheet(df, create_prompt_folder_id)
