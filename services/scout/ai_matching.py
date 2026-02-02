import re
from clients import gemini_client
from collections import defaultdict, Counter

def format_prompt(judge_condition, required_condition, welcome_condition, job_title):
  return f"""
            あなたは優秀なリクルーターです。企業のリクルーターとして、添付した募集求人(ファイル名：{job_title})に対しての候補者にダイレクトスカウトを送信します。
            【PDFの扱いについて】
            ・ファイル名：{job_title}は募集求人として読み取ってください。
            ・ファイル名：{job_title}以外のファイルは候補者情報として読み取ってください。
            ・添付するPDFには複数の候補者の職歴が載っている場合があります。
            ・PDFに記載されている候補者情報を全員分読み取ってください。
            ・判定はファイル名：{job_title}以外のファイルに対して行ってください。

            【IDの取り扱いについて】
            ・ファイル名に数字が含まれているので、その数字を「id」として扱ってください。
            ・ファイル名に数字が含まれておらず、1つのPDFに複数の候補者情報が記載されている場合は、各候補者の最初の情報として「BU」から始まる9文字のIDが記載されています。
              → この9文字のIDを「id」として扱ってください。

            スカウト業務を以下のSTEP1、STEP2の流れで対応してください。

            【STEP 1：候補者ごとの送付可否判定】
            各候補者について以下の形式で判定してください。
            - STEP1における必須要件を満たすか(required_condition): "A" or "B" or "C"
            - STEP1における歓迎要件を満たすか(welcome_condition): "A" or "B" or "C"
            - STEP1の結果(候補者の評価結果)(evaluation_result): "A" or "B" or "C"
            - 必須要件、歓迎要件の結果を踏まえた候補者の評価理由(evaluation_reason): 判定の理由（200文字以内）

            ・複数の候補者情報が記載されたPDFを添付します。それぞれの候補者についてA/B/Cの判定をしてください。
            判定条件は次の通りです。
              {judge_condition}

            <必須要件>
              {required_condition}

            <歓迎要件>
              {welcome_condition}

            【STEP 2：以下の条件、および例を参考に、添付ファイルの候補者全員分、声をかけた背景を伝える文章を作成してください。（STEP1の結果、C評価の候補者についても作成すること）】
            ## 募集求人
            添付ファイル：{job_title}
            ## 文章作成時の条件
            ・180字前後で作成する
            ・1行目は「特に、」で固定する
            ・2~4行目は、候補者の経験の中でも特に活かせるスキル・経験を箇条書きで3つ挙げる
            ・5行目は、2~4行目で上げたスキルが弊社で活かせるということに繋げる文章

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
                  "id": "<PDFのファイル名>",
                  "required_condition"：true or false,
                  "welcome_condition"：true or false,
                  "evaluation_reason"："理由",
                  "evaluation_result"：A or B or C,
                  "scout_message"："文面",
                }}
              ]
            }}

            ・すべての候補者を this JSON の配列にまとめて返してください。
            ・これは最終出力であり、途中思考は出力しないでください。
            """


def create_list_by_gemini(pdfs, judge_condition, required_condition, welcome_condition, job_pdf, temperature):
  job_title = ""
  for _, original_name in job_pdf:
    job_title = original_name

  prompt = format_prompt(judge_condition, required_condition, welcome_condition, job_title)
  results = gemini_client.request_with_files_by_parallel(prompt, pdfs, job_pdf, temperature)

  finally_results = get_majority_decision(results)
  return finally_results


def extract_numeric_id(id: str) -> str:
  # 数字のみかチェック
  if id.isdigit():
    return id
  
  # BUで始まる場合はそのまま返す（抽出処理をスキップ）
  if id.startswith("BU"):
    return id
  
  # 数字以外が含まれている場合は数字のみを抽出
  numeric_only = re.sub(r'\D', '', id)
  return numeric_only


def get_majority_decision(ai_results):
  results_by_id = defaultdict(list)
  for inquiry in ai_results:
    for record in inquiry.results:
      # IDから数字のみを抽出
      numeric_id = extract_numeric_id(record.id)
      results_by_id[numeric_id].append(record)

  final_majority_results = []
  for id, records in results_by_id.items():
    counts = Counter(record.evaluation_result for record in records)
    majority_result = counts.most_common(1)[0][0] if counts else "N/A"

    majority_record = next(
      (record for record in records if record.evaluation_result == majority_result),
      None
    )
    if majority_record:
      final_majority_results.append(majority_record)

    print(f"ID: **{id}** の多数決結果: **{majority_result}**")

  return final_majority_results
