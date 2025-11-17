import json
from clients import openai_client

def format_text(condition1, condition2):
  return f"""
            あなたは採用スカウト担当として、複数のPDF（候補者書類）に対して個別に評価を行います。
            【PDFの扱いについて】
            ・あなたには複数のメッセージで PDF が渡されます。
            ・それぞれの PDF は1ファイル＝1候補者です。
            ・各 PDF のメッセージ内に “filename: XXXXX.pdf” を記載しています。
              → このファイル名を「id」として扱ってください。


            【STEP 1：候補者ごとの送付可否判定】
            各PDF（候補者）について以下の形式で判定してください。
            - 判定: "OK" or "NG"
            - 理由: 判定の理由（200文字以内）
            ・複数の候補者PDFを添付します。それぞれの候補者について送付OK/NGの判定をしてください。
            判定条件は次の通りです。
              ▼ 以下の条件のうち **1つでも満たさない場合は NG判定**
              {condition1}

              ▼ 以下の条件のうち **1つでも当てはまる場合は NG判定**
              {condition2}

            【STEP 2：スカウト文面】
            STEP1で「OK」だった候補者のみ、
            添付した候補者PDFの情報を参照し、
            180字以内で「お声がけした背景」を作成してください。

            NGの場合は スカウト文面="" としてください。

            【出力形式（必ずこの通りの純粋なJSONで出力）】

            {{
              "result": [
                {{
                  "id": "<PDFのファイル名>",
                  "判定": "OK または NG",
                  "理由": "理由",
                  "スカウト文面": "スカウト文面（OKの場合）"
                }}
              ]
            }}

            ・すべての候補者を this JSON の配列にまとめて返してください。
            ・これは最終出力であり、途中思考は出力しないでください。
            """


def create_list(pdfs, condition1, condition2):
  prompt = format_text(condition1, condition2)

  res_json = openai_client.call_api(prompt, pdfs)
  res = res_json.output[0].content[0].text
  print(res_json)
  try:
      # 余分な文字列を削除
      cleaned_res = res.replace('```json', '').replace('```', '').strip()
      parsed_json = json.loads(cleaned_res)
      return parsed_json
  except json.JSONDecodeError as e:
      print(f"JSON Parse Error: {str(e)}")
      print("Invalid JSON content:", res)
      raise
