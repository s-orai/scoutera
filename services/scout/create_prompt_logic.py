from clients import gemini_client

from services.scout.prompts import PROMPT_CREATE_PROMPT


def format_prompt(pdfs_A, pdfs_B, pdfs_C, comment_B, comment_C, job_title):
  return PROMPT_CREATE_PROMPT.format(
    pdfs_A=pdfs_A,
    pdfs_B=pdfs_B,
    pdfs_C=pdfs_C,
    comment_B=comment_B,
    comment_C=comment_C,
    job_title=job_title,
  )


def create_list_by_gemini(pdfs_a, pdfs_b, pdfs_c, comment_b, comment_c, job_pdf):
  job_title = ""
  for _, original_name in job_pdf:
    job_title = original_name

  pdfs_a_titles = extract_original_name(pdfs_a)
  pdfs_b_titles = extract_original_name(pdfs_b)
  pdfs_c_titles = extract_original_name(pdfs_c)

  prompt = format_prompt(pdfs_a_titles, pdfs_b_titles, pdfs_c_titles, comment_b, comment_c, job_title)
  pdfs = pdfs_a + pdfs_b + pdfs_c
  result = gemini_client.request_for_create_prompt(prompt, pdfs, job_pdf)

  return result

def extract_original_name(pdfs):
  """
  一時ファイル情報のリストから元のファイル名だけを取り出してリストで返す。
  pdfs そのものは破壊的に変更しない。
  """
  names = []
  for _, original_name in pdfs:
    names.append(original_name)
  return names
