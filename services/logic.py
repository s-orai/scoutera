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


def main_by_gemini(judge_condition, required_condition, welcome_condition, pdfs, job_pdf, temperature):
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

  return export_to_spredsheet(df)