from openai import OpenAI
import streamlit as st
import re

api_key = st.secrets["open_ai"]["api_key"]
client = OpenAI(api_key=api_key)
model = "gpt-5-mini-2025-08-07"

gemini_api_key = st.secrets["gemini"]["api_key"]
gemini_client = OpenAI(api_key=gemini_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
gemini_model = "gemini-2.5-flash"



def call_api(prompt, pdfs):
  if not prompt:
    raise RuntimeError(f"プロンプトが入力されていません。")
  elif not pdfs:
    raise RuntimeError(f"pdfが空です")
  input = create_input(prompt, pdfs)
  return client.responses.create(
        model=model,
        input=input,
        store=True,
  )


def call_gemini_api(prompt, pdfs):
  if not prompt:
    raise RuntimeError(f"プロンプトが入力されていません。")
  elif not pdfs:
    raise RuntimeError(f"pdfが空です")
  input = create_input(prompt, pdfs)
  return gemini_client.responses.create(
        model=model,
        input=input,
        store=True,
  )

def format_pdf(files):
  inputs = []
  for file in files:
    pdf = client.files.create(
        file=file,    # ← そのまま渡せる
        purpose="user_data"
    )
    filename = re.match(r"^(.*?)(?:\.pdf)$", pdf.filename).group(1)
    inputs.append(
      {
        "role": "user",
        "content": [
            {
                "type": "input_file",
                "file_id": pdf.id
            },
            # {
            #     "type": "input_text",
            #     "text": f"これは{filename}の書類です。内容を読み込んでください。filename: {filename}"
            # }
        ]
      }
    )

  return inputs

def create_input(prompt, pdfs):
  inputs = format_pdf(pdfs)
  inputs.append(
    {
      "role": "user",
      "content": [{"type": "input_text", "text": prompt}]
    }
  )
  return inputs

