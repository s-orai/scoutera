from services.screening.prompts import PROMPT_SCREENING


def format_prompt(required_condition, welcome_condition, jd_title, candidate_info="", candidate_titles=None):
  if candidate_titles is None:
    candidate_titles = []
  candidate_titles_str = ", ".join(candidate_titles)
  return PROMPT_SCREENING.format(
    required_condition=required_condition,
    welcome_condition=welcome_condition,
    jd_title=jd_title,
    candidate_info=candidate_info,
    candidate_titles_str=candidate_titles_str,
  )