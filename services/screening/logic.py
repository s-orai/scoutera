from clients import gemini_client
from models import ScreeningResultsContainer
from services.screening import preparation_ai
from utils import get_majority_decision_single
import pandas as pd

def screening(candidate_info, required_condition, welcome_condition, candidate_pdfs, jd_pdf):

  for _, original_name in jd_pdf:
    jd_title = original_name

  candidate_pdf_titles = []
  for _, original_name in candidate_pdfs:
    candidate_pdf_titles.append(original_name)

  prompt = preparation_ai.format_prompt(required_condition, welcome_condition, jd_title, candidate_info, candidate_pdf_titles)
  results = gemini_client.request_with_files_by_parallel(
    prompt, 
    candidate_pdfs, 
    jd_pdf, 
    ScreeningResultsContainer,
    is_screening=True
  )

  finally_result = get_majority_decision_single(results)
  data_dicts = finally_result.model_dump()
  df = pd.DataFrame([data_dicts])
  return df.iloc[0]