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

            【STEP 2：以下の条件、および例を参考に、添付ファイルの候補者全員分、声をかけた背景を伝える文章を作成してください。（STEP1の結果、C評価の候補者についても作成すること）】
            ## 文章作成時の条件
            ・候補者の経験の中でも特に活かせるスキル・経験を箇条書きで挙げ(3~4個)、それが弊社で活かせることを伝える(180文字程度)
            ・箇条書き項目ごとに改行を入れること

            ## 文章の作成例
            特に、
            ・高負荷APIの安定化
            ・障害時の切り分けを可能にするログ設計
            ・Next.js / Node.js を用いた刷新経験
            ・決済系の深い実装経験（楽天Edy・レシート印刷など）
            は、LINE注文・管理画面・決済まわりを含む当社のシステム刷新の中核にそのまま活かせる領域です。

            【出力形式（必ずこの通りの純粋なJSONで出力）】
            {{
              "result": [
                {{
                  "ID": "<PDFのファイル名>",
                  "STEP1における必須要件を満たすか"：true or false,
                  "STEP1における歓迎要件を満たすか"：true or false,
                  "必須要件、歓迎要件の結果を踏まえた候補者の評価理由"："理由",
                  "判定": "A または B または C",
                  "STEP1の結果(候補者の評価結果)"：A or B or C,
                  "STEP2の結果(声がけした背景の文章)"："文面"
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