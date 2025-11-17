from openai import OpenAI
import streamlit as st

api_key = st.secrets["open_ai"]["api_key"]
client = OpenAI(api_key=api_key)
model = "gpt-4.1-mini"


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
        temperature=0
  )

def format_pdf(files):
  inputs = []
  for file in files:
    pdf = client.files.create(
        file=file,    # ← そのまま渡せる
        purpose="user_data"
    )
    inputs.append(
      {
        "role": "user",
        "content": [
            {
                "type": "input_file",
                "file_id": pdf.id
            },
            {
                "type": "input_text",
                "text": f"これは{pdf.filename}の書類です。内容を読み込んでください。"
            }
        ]
      }
    )

  print("pdfのリスト")
  print(inputs)

  return inputs

def create_input(prompt, pdfs):
  inputs = format_pdf(pdfs)
  inputs.append(
    {
      "role": "user",
      "content": [{"type": "input_text", "text": prompt}]
    }
  )
  print("最終系")
  print(inputs)
  return inputs

