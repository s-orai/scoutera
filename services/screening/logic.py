from clients import gemini_client
from models import ResultsContainer
from services.screening import preparation_ai
from collections import Counter
import pandas as pd

def screening(candidate_info, required_condition, welcome_condition, candidate_pdfs, jd_pdf):

  for _, original_name in jd_pdf:
    jd_title = original_name

  candidate_pdf_titles = []
  for _, original_name in candidate_pdfs:
    candidate_pdf_titles.append(original_name)

  prompt = preparation_ai.format_prompt(required_condition, welcome_condition, jd_title, candidate_info, candidate_pdf_titles)
  results = gemini_client.request_with_files_by_parallel(prompt, candidate_pdfs, jd_pdf, ResultsContainer)

  finally_result = _get_majority_decision(results)
  data_dicts = finally_result.model_dump()
  df = pd.DataFrame([data_dicts])
  return df.iloc[0]


def _get_majority_decision(ai_results):
  """
  一人の候補者に対する3件のスクリーニング結果から多数決を取る
  
  Args:
      ai_results: List[ResultsContainer] - 3回の実行結果のリスト
  
  Returns:
      単一のレコード（多数決結果）
  """
  # 全ての結果レコードを収集
  all_records = []
  for inquiry in ai_results:
    for record in inquiry.results:
      all_records.append(record)
  
  if not all_records:
    print("⚠️ スクリーニング結果が空です")
    return None
  
  # evaluation_resultで多数決を取る
  counts = Counter(record.evaluation_result for record in all_records)
  majority_result = counts.most_common(1)[0][0] if counts else "N/A"
  
  # 多数決結果に一致する最初のレコードを返す
  majority_record = next(
    (record for record in all_records if record.evaluation_result == majority_result),
    None
  )
  
  print(f"✅ スクリーニング多数決結果: **{majority_result}** (投票: {dict(counts)})")
  
  return majority_record