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



def main(condition1, condition2, condition3, pdfs):
  json = ai_matching.create_list(pdfs, condition1, condition2, condition3)
  df = pd.DataFrame(json['result'])

  return export_to_spredsheet(df)





def main_by_gemini(condition1, condition2, condition3, pdfs, job_pdf, temperature):
  json = ai_matching.create_list_by_gemini(pdfs, condition1, condition2, condition3, job_pdf, temperature)
  df = pd.DataFrame(json['result'])

  return export_to_spredsheet(df)