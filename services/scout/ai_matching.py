from clients import gemini_client
from models.scout_models import ResultsContainer
from utils import get_majority_decision_by_id

from services.scout.prompts import PROMPT_SCOUT_MATCHING, PROMPT_SCOUT_MATERIAL


def format_prompt(required_condition, welcome_condition, job_title):
  return PROMPT_SCOUT_MATCHING.format(
    required_condition=required_condition,
    welcome_condition=welcome_condition,
    job_title=job_title,
  )


def create_list_by_gemini(pdfs, required_condition, welcome_condition, job_pdf):
  job_title = ""
  for _, original_name in job_pdf:
    job_title = original_name

  prompt = format_prompt(required_condition, welcome_condition, job_title)
  results = gemini_client.request_with_files_by_parallel(
    prompt, 
    pdfs, 
    job_pdf, 
    ResultsContainer
  )

  finally_results = get_majority_decision_by_id(results)
  return finally_results

def format_prompt_for_scout_material(pdf_title):
  return PROMPT_SCOUT_MATERIAL.format(pdf_title=pdf_title)
