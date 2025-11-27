import json
from clients import openai_client, gemini_client

def format_text(condition1, condition2, condition3):
  return f"""
            あなたは採用スカウト担当として、複数の候補者に対して個別に評価を行います。
            【PDFの扱いについて】
            ・添付するPDFには複数の候補者の職歴が載っています。
            ・PDFに記載されている候補者情報を全員分読み取ってください。

            【IDの取り扱いについて】
            ・ファイル名が数字の場合はその数字を「id」として扱ってください。
            ・1つのPDFに複数の候補者情報が記載されている場合、各候補者の最初の情報として「BU」から始まる9文字のIDが記載されています。
              → この9文字のIDを「id」として扱ってください。


            【STEP 1：候補者ごとの送付可否判定】
            各候補者について以下の形式で判定してください。
            - 判定: "A" or "B" or "C"
            - 理由: 判定の理由（200文字以内）
            ・複数の候補者情報が記載されたPDFを添付します。それぞれの候補者についてA/B/Cの判定をしてください。
            判定条件は次の通りです。
              {condition1}

            <必須要件>
              {condition2}

            <歓迎要件>
              {condition3}

            【STEP 2：スカウト文面】
            添付した候補者PDFの情報を参照し、
            180字以内で「お声がけした背景」を作成してください。

            【出力形式（必ずこの通りの純粋なJSONで出力）】

            {{
              "result": [
                {{
                  "id": "<PDFのファイル名>",
                  "判定": "A または B または C",
                  "理由": "理由",
                  "スカウト文面": "スカウト文面"
                }}
              ]
            }}

            ・すべての候補者を this JSON の配列にまとめて返してください。
            ・これは最終出力であり、途中思考は出力しないでください。
            """


def create_list(pdfs, condition1, condition2, condition3):
  prompt = format_text(condition1, condition2, condition3)

  res_json = openai_client.call_api(prompt, pdfs)
  res = res_json.output[1].content[0].text
  try:
      # 余分な文字列を削除
      cleaned_res = res.replace('```json', '').replace('```', '').strip()
      parsed_json = json.loads(cleaned_res)
      return parsed_json
  except json.JSONDecodeError as e:
      print(f"JSON Parse Error: {str(e)}")
      print("Invalid JSON content:", res)
      raise


def create_list_by_gemini(pdfs, condition1, condition2, condition3):
  prompt = format_text(condition1, condition2, condition3)
  res_json = gemini_client.call_api(pdfs, prompt)
  print(res_json.text)
  try:
      parsed_json = json.loads(res_json.text)
      return parsed_json
  except json.JSONDecodeError as e:
      print(f"JSON Parse Error: {str(e)}")
      print("Invalid JSON content:", res_json)
      raise