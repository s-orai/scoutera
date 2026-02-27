from services.scout import ai_matching
import pandas as pd
from services.scout import create_prompt_logic
from clients import google_client
from clients import gemini_client
from config import get_google_config

_google_config = get_google_config()
scout_folder_id = _google_config["scout_folder_id"]
create_prompt_folder_id = _google_config["create_prompt_folder_id"]
scout_material_folder_id = _google_config["scout_material_folder_id"]

# スプレッドシートへエクスポート
def export_to_spredsheet(df, folder_id):
    client = google_client.GoogleClient()

    # 1. 新しいスプレッドシートを作成（共有ドライブのフォルダ内）
    spreadsheet_id = client.create_spreadsheet(folder_id)

    # 2. データを書き込み
    spreadsheet_url = client.write_data(spreadsheet_id, df)

    return spreadsheet_url


def main(required_condition, welcome_condition, pdfs, job_pdf):
  json = ai_matching.create_list_by_gemini(pdfs, required_condition, welcome_condition, job_pdf)
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

def create_prompt(pdfs_A, pdfs_B, pdfs_C, comment_B, comment_C, job_pdf):
  json = create_prompt_logic.create_list_by_gemini(pdfs_A, pdfs_B, pdfs_C, comment_B, comment_C, job_pdf)

  data_dicts = [json.model_dump()]
  df = pd.DataFrame(data_dicts)

  return df.iloc[0]

def create_scout_material(job_pdf):
  for _, original_name in job_pdf:
    pdf_title = original_name

  prompt = ai_matching.format_prompt_for_scout_material(pdf_title)
  result = gemini_client.request_with_files_for_scout_material(prompt, job_pdf)
  data_dicts = result.model_dump()
  df = pd.DataFrame([data_dicts])
  df.columns = [
    "募集ポジションにマッチする候補者のペルソナ",
    "経験職種",
    "経験業種",
    "検索キーワード",
    "現年収",
    "希望年収",
    "スカウト件名",
    "スカウト文面"
  ]

  return export_to_spredsheet(df, scout_material_folder_id)