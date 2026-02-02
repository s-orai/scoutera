import re
from clients import gemini_client
from collections import defaultdict, Counter

def format_prompt_for_business_description(company_info):
  return f"""
            あなたは企業の採用担当として、募集ポジションに対する求人票を作成しています。
            候補者を惹きつける目的で、求人票の一部の会社説明、事業紹介の文章を作成してください。
            以下の会社情報、作成条件に基づき、文章を作成してください。

            # 会社情報
            {company_info}

            # 作成条件
            以下の「企業理念」「事業紹介」「事業の詳細」の3項目を、それぞれ構成と制約条件に基づいて作成してください
            ## 企業理念
            ### 構成
            ・会社として目指しているゴール、理念の説明
            ・ミッション・ビジョン・バリューの説明
            ### 作成時の制約条件・注意事項
            ・250字程度で作成する
            ・会社が目指すゴールや理念に、候補者の共感を得られる文章にする
            ・業界外の人でも理解できるよう、専門用語は避ける、もしくは補足を入れる
            ## 事業紹介
            ### 構成
            ・一言で事業について説明
            ・事業領域、向き合う課題、社会的な意義
            ・事業の独自性、競合優位性
            ・事業の今後の成長性、これまでの実績、直近のニュース（リリース等）
            ### 作成時の制約条件・注意事項
            ・250字程度で作成する
            ・事業が複数ある場合でも、抽象化し簡易的な説明にまとめる
            ・事業をする意義に、候補者の共感を得られる文章にする
            ・業界外の人でも理解できるよう、専門用語は避ける、もしくは補足を入れる
            ## 事業の詳細
            ### 構成
            ・サービス名
            ・提供しているサービス内容の詳細
            ・顧客、ターゲット説明
            ・課題と解決策について
            ・独自性や強みについて
            ・導入実績
            ・今後の展開
            ### 作成時の制約条件・注意事項
            ・事業が複数ある場合は、それぞれについて記述を作成する
            ・構成をそれぞれ出力するのではなく、文章で繋げて出力する
            ・業界外の人でも理解できるよう、専門用語は避ける、もしくは補足を入れる
            ・事業としての意義や成長性をアピールする文章にする

              # 文章作成例
              ## 例: 株式会社JULIA IVY
              ### 企業理念
              すべての人生に、一歩踏み出す勇気と感動の瞬間を提供します。
              株式会社JULIA IVYは、「美容業界に新しい職業と文化を生み出す会社」です。創業のきっかけとなった眉癖改善技術 「HBL（ハリウッドブロウリフト）」 を原点に、美容業界に新しい職業と文化を生み出してきました。「HBL」では、これまで存在しなかった「眉毛をプロに任せる」という新しい文化を作り、かつてネイルサロンが当たり前になり、ネイリストが憧れの職業になったように、「ブロウアーティスト」という職業を、誰もが憧れる存在へと押し上げていく挑戦を続けています。
              ### 事業紹介
              また、韓国のエステティックスキンケアブランド 「TROIAREUKE（トロイアルケ）」 の日本展開では、「かかりつけエステ」という新しい文化を根付かせることに挑戦しています。2025年3月には自社コスメブランド 「HBL BEAUTY」 をローンチし、早くもベストコスメを多数受賞。7月にはHBLをリブランディングし、世界観を再構築しました。さらに現在はTROIAREUKEの日本展開を本格推進するなど、次々と新たなチャレンジを仕掛けています。
              ### 事業の詳細
              ・HBL（ハリウッドブロウリフト）
              国産の専用セッティング剤とスタイリング剤、特殊なオリジナルワックスの技術によって、眉毛の生えグセを改善し、日本人特有の横に向いて生えている眉毛の癖など、毛流れを根本的に改善するアイブロウソリューション®です。国内のアイブロウ業界には、アートメイクをはじめ、眉毛ワックスや美眉の似合わせが存在していましたが、ハリウッドブロウリフトは従来のアイブロウの形だけ整えるという概念を超え、「眉整形」と呼ばれるほど、眉毛の毛流れを整える、今までになかった男女共に支持される次世代アイブロウ技術です。

              ・TROIAREUKE（トロイアルケ）
              TROIAREUKEは美容大国・韓国で1985年に誕生し、40年の歴史を誇るプロフェッショナル向けスキンケアブランドです。
              皮膚科学に基づいた高機能スキンケアを提供し、エステサロンや美容クリニック向けに開発されたカスタマイズ可能なスキンケアが特徴で、
              「痛い・辛いダウンタイムの時代は終わり、優しく、自分に合ったケアで根本から肌を整える」という新しいスキンケアの概念を提案しています。
              弊社は日本総代理店として、その最先端のスキンケアソリューションを日本市場へ展開しています。

              ・HBL BEAUTY
              2025年3月にローンチした、眉に特化した独自コスメブランドです。
              「小さな眉の大きな力眉を変えれば心が変わり、人生が変わる」をコンセプトに、HBL事業で700万人以上の眉を見てきた知見をもとにあらゆる眉や顔立ちの悩みに応えるために製作。
              ローンチ初年度でViVi、美的、SPURなど主要美容誌でベストコスメ23冠を受賞。SNSやメディアでも話題を呼び、急成長しています。

              -----
              以上を踏まえ、求人票求人票の一部の会社説明、事業紹介の文章を作成してください。
              以下の項目を出力形式に従って出力してください。
              1. 会社名
              2. 事業サービス名
              3. 企業理念
              4. 事業紹介
              5. 事業の詳細

            【出力形式（必ずこの通りの純粋なJSONで出力）】
            {{
              "company_name": 会社名,
              "business_service_name": 事業サービス名,
              "company_philosophy": 企業理念,
              "business_introduction": 事業紹介,
              "business_detail": 事業の詳細
            }}

            ・これは最終出力であり、途中思考は出力しないでください。
            """

def format_prompt_for_jd(company_info, text, jd_title):
  return f"""
            あなたは企業の採用担当として、募集ポジションに対する求人票を作成しています。
            求人票の要となる、募集背景、仕事内容、募集要項のパートを作成してください。
            以下の募集ポジション情報と作成条件に基づき、文章を作成してください。

            【PDFの扱いについて】
            ・ファイル名：{jd_title}は求人票として読み取ってください。

            # 募集ポジション情報
            ## 会社情報
            {company_info}
            ## 募集ポジションの詳細
            {text}

            # 作成条件
            以下の「募集背景」「仕事内容」「必須要件」「歓迎要件」「求める人物像」の5項目を、それぞれ構成と制約条件に基づいて作成してください
            ## 募集背景
            ### 構成
            ・事業ロードマップ
            ・部門としての目標
            ・現在の体制
            ・不足しているピース
            ### 作成時の制約条件・注意事項
            ・200字程度で作成する
            ・これをみた候補者に募集ポジションが必要である意図が伝わる文章にする
            ・事業成長に向けた前向きな募集であることが伝わるようにする
            ## 仕事内容
            ＜ヒアリング項目参照してマスタから引っ張ってくる＞
            ## 必須要件
            ### 構成
            ・書類選考でスクリーニング基準となるスキルや経験
            ・仕事内容で示した職務を果たすために入社時点で必須なスキルや、具体的な職種の経験
            ・その他業務ツールや環境面で、入社時に必須と判断する経験（開発技術や、SaaSツールなど）
            ### 作成時の制約条件・注意事項
            ・箇条書きで1文ずつ記載する
              - 1文あたり30字程度で作成する
            ## 歓迎要件
            ### 構成
            ・入社時点で必須ではないが加点される（あったら嬉しい）スキルや職種の経験
            ### 作成時の制約条件・注意事項
            ・箇条書きで1文ずつ記載する
              - 1文あたり30字程度で作成する
            ## 求める人物像
            ### 構成
            ・募集ポジションにマッチするマインドやキャリア志向
            ・企業の理念やバリューに適したマインドやキャリア志向
            ### 作成時の制約条件・注意事項
            ・箇条書きで1文ずつ記載する
              - 1文あたり30字程度で作成する

              # 作成例
              ファイル「{jd_title}」

              -----
              以上を踏まえ、求人票の要となる、募集背景、仕事内容、募集要項パートの文章を作成してください。
              以下の項目を出力形式に従って出力してください。
              1. 募集背景
              2. 募集職種
              3. 必須要件
              4. 歓迎要件
              5. 求める人物像

              【出力形式（必ずこの通りの純粋なJSONで出力）】
              {{
                "background": 募集背景,
                "job_category": 募集職種,
                "required_requirement": 必須要件,
                "welcome_requirement": 歓迎要件,
                "character_statue": 求める人物像
              }}

              ・これは最終出力であり、途中思考は出力しないでください。
            """


# def create_list_by_gemini(pdfs, judge_condition, required_condition, welcome_condition, job_pdf, temperature):
#   job_title = ""
#   for _, original_name in job_pdf:
#     job_title = original_name

#   prompt = format_prompt(judge_condition, required_condition, welcome_condition, job_title)
#   results = gemini_client.request_with_files_by_parallel(prompt, pdfs, job_pdf, temperature)

#   finally_results = get_majority_decision(results)
#   return finally_results


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
