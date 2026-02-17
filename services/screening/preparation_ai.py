def format_prompt(required_condition, welcome_condition, jd_title, candidate_info="", candidate_titles=[]):
  return f"""
            あなたは優秀なリクルーターです。企業のリクルーターとして、添付した募集求人(ファイル名：{jd_title})に対しての候補者の書類選考を行います。

            【PDFの扱いについて】
            ・ファイル名：{jd_title}は募集求人として読み取ってください。
            ・ファイル名：{candidate_titles}のファイル群は候補者情報として読み取ってください。
            ・添付する候補者PDFは複数の場合があります。

            以下の条件に従って、募集ポジションに対して候補者が書類選考通過基準を満たすかどうか、評価をA, B, Cで行ってください。またその理由も合わせて出力してください。

            ## 候補者情報
            {candidate_info}
            {", ".join(candidate_titles)}

            ## 評価基準
            ・A評価：必須要件を満たし、かつ歓迎要件を一部以上満たす場合
            ・B評価：必須要件は満たすが、歓迎要件は満たさない場合
            ・C評価：必須要件を一部でも満たさない場合
            ### 必須要件
            {required_condition}
            ### 歓迎要件
            {welcome_condition}

            ## 判定時の注意事項
            ・候補者情報が少ない場合は情報からスキルを推測して判定すること
              - (例)候補者情報が、年齢・現職社名とポジションのみの場合→一般的なキャリアと年齢と職種からの推測も踏まえ、要件を満たすかどうか反映する

            —-
            以上を踏まえ、以下の項目を出力してください。
            1. 候補者の評価理由：text
            2. 必須要件を満たすか：true or false
            3. 歓迎要件を満たすか：true or false
            4. 候補者の評価結果：A or B or C

            【出力形式（必ずこの通りの純粋なJSONで出力）】
            {{
              "evaluation_reason": 候補者の評価理由,
              "required_condition": 必須要件を満たすか,
              "welcome_condition": 歓迎要件を満たすか,
              "evaluation_result": 候補者の評価結果,
            }}

            ・これは最終出力であり、途中思考は出力しないでください。
  """