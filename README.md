# Scout Automation

採用・スカウト業務を効率化するためのツール群です。Streamlit ベースの Web アプリと、バッチ・ユーティリティスクリプトで構成されています。

---

## 目次

- [概要](#概要)
- [セットアップ](#セットアップ)
- [起動方法](#起動方法)
- [ツール一覧](#ツール一覧)
- [プロジェクト構成](#プロジェクト構成)
- [設定・シークレット](#設定シークレット)

---

## 概要

本プロジェクトは次の 3 つのメイン機能を提供します。

| 機能 | 説明 |
|------|------|
| **スカウト効率化** | 候補者 PDF と求人票を AI で評価し、ピックアップ・プロンプト作成・スカウト素材出力を行う |
| **求人票作成** | 会社情報・ヒアリング・参考求人票から募集要項や会社・事業説明文を生成する |
| **書類選考** | 候補者情報・求人票・必須・歓迎要件に基づき書類選考結果（評価理由・結果）を出力する |

認証は `streamlit-authenticator` で行い、ログイン後に上記メニューから各ツールを利用できます。

---

## セットアップ

### 必要環境

- Python 3.x
- 依存パッケージ: `requirements.txt` を参照

```bash
pip install -r requirements.txt
```

### 主な依存

- **Streamlit** … Web UI
- **google-genai** … Gemini API（候補者評価・求人票生成など）
- **OpenAI** … 一部機能・バッチで利用
- **gspread / google-api-python-client** … スプレッドシート・Drive 連携
- **PyMuPDF (fitz)** … PDF 解析
- **easyocr** … OCR（スタンドアロンスクリプト用）

---

## 起動方法

Web アプリの起動:

```bash
streamlit run app.py
```

ブラウザで開き、ログイン後にサイドバーから「スカウト効率化」「求人票作成」「書類選考」を選択して利用します。

---

## ツール一覧

### 1. スカウト効率化（スカウト候補者ピックアップツール）

**画面:** ログイン後 → サイドバー「スカウト効率化」

| タブ | 機能 | 入力 | 出力 |
|------|------|------|------|
| **候補者ピックアップ** | 候補者 PDF と求人票を AI で評価し、一覧をスプレッドシートに出力 | 候補者 PDF（複数）、求人票 PDF、必須要件・歓迎要件（テキスト） | Google スプレッドシート URL（評価理由・STEP1/STEP2 結果など） |
| **プロンプト作成** | A/B/C 評価サンプルと求人票から、評価基準のプロンプトを生成 | A/B/C 評価候補者 PDF、求人票 PDF、B/C 評価コメント | スプレッドシート（必須要件・スキル差分等） |
| **スカウト素材出力** | 求人票 PDF からスカウト用の素材を抽出・整形 | 求人票 PDF | スプレッドシート URL |

- 実装: `services/scout/main.py`, `services/scout/logic.py`, `services/scout/ai_matching.py`, `services/scout/create_prompt_logic.py`
- AI: Gemini / 設定は `config/settings.py` の `get_gemini_config()` 経由

---

### 2. 求人票作成アシストツール

**画面:** ログイン後 → サイドバー「求人票作成」

| タブ | 機能 | 入力 | 出力 |
|------|------|------|------|
| **求人票作成** | 会社情報・ヒアリング・参考求人票 PDF から募集要項を生成 | 会社情報、ヒアリング内容、参考求人票 PDF（複数）、temperature | 募集背景・募集職種・仕事内容・必須要件・歓迎要件・求める人物像（画面表示） |
| **会社・事業説明** | 会社情報（テキスト or URL）から会社・事業説明文を生成 | 会社情報（複数 URL 可）、temperature | 会社名・事業サービス名・企業理念・事業紹介・事業の詳細（画面表示） |

- 実装: `services/jd/main.py`, `services/jd/logic.py`
- AI: Gemini（求人票・会社説明）、必要に応じて OpenAI
- 会社情報は URL の場合、`utils/web_utils.scrape_page_text` でスクレイピングしてからプロンプトに渡す

---

### 3. 書類選考アシストツール

**画面:** ログイン後 → サイドバー「書類選考」

| 項目 | 内容 |
|------|------|
| **機能** | 候補者（PDF またはテキスト）と求人票・必須・歓迎要件から、書類選考結果を生成 |
| **入力** | 候補者情報（テキスト）、候補者 PDF（任意）、求人票 PDF、必須要件・歓迎要件 |
| **出力** | 評価理由、必須要件・歓迎要件の結果、評価結果（画面表示） |

- 実装: `services/screening/main.py`, `services/screening/logic.py`
- AI: Gemini（並列リクエスト）、`utils.ai_utils.get_majority_decision_single` で集約

---

### 4. スタンドアロンスクリプト・ユーティリティ

アプリからは起動せず、必要に応じて手動実行するスクリプトです。

| ファイル | 用途（概要） |
|----------|----------------|
| **batch_job.py** | Google Drive から候補者 PDF を取得（DODAX/AMBI 等フォルダ）、ダウンロード・CSV 出力などバッチ処理。OpenAI・Drive API・環境変数（`ROOT_FOLDER_ID`, `DODAX_FOLDER_ID`, `AMBI_FOLDER_ID` 等）を使用 |
| **handle_structure_mapping.py** | EasyOCR + PyMuPDF で PDF からテキスト抽出し、正規表現で候補者情報（年齢・学歴・年収・スキル・希望条件など）を構造化。スタンドアロン用のマッピング・検証用 |
| **sample_extract_pdf.py** | PDF 抽出のサンプル・動作確認用 |
| **test_extract.py** | 抽出処理のテスト用 |

※ 上記スクリプトは `.env` や `service-account.json` など、アプリとは別の設定が必要な場合があります。

---

## プロジェクト構成

```
scout_automation/
├── app.py                    # Streamlit エントリポイント（認証・メニュー・ページ振り分け）
├── config/
│   ├── __init__.py
│   └── settings.py           # 設定・シークレット取得（Gemini / OpenAI / Google / 認証）
├── clients/
│   ├── gemini_client.py      # Gemini API 呼び出し
│   ├── google_client.py      # スプレッドシート・Drive 操作
│   └── openai_client.py      # OpenAI API 呼び出し
├── models/
│   ├── jd_models.py         # 求人票まわり Pydantic モデル
│   ├── scout_models.py      # スカウトまわりモデル
│   └── screening_models.py  # 書類選考まわりモデル
├── services/
│   ├── jd/                  # 求人票作成・会社説明
│   ├── scout/               # スカウト候補者ピックアップ・プロンプト・スカウト素材
│   └── screening/           # 書類選考
├── utils/
│   ├── ai_utils.py          # AI 結果の集約（多数決等）
│   ├── file_utils.py        # アップロード・一時ファイル
│   ├── ui_utils.py          # Streamlit UI（コードブロック表示等）
│   └── web_utils.py         # スクレイピング（会社情報取得）
├── batch_job.py             # バッチ処理（Drive 取得等）
├── handle_structure_mapping.py  # PDF 構造化マッピング
├── sample_extract_pdf.py
├── test_extract.py
└── requirements.txt
```

- **設定**は `config/settings.py` に集約され、`st.secrets` を参照するのはこのモジュール内のみです。
- **クライアント**（Gemini / Google / OpenAI）は `clients/` でラップし、設定は `config` から取得します。

---

## 設定・シークレット

Web アプリは Streamlit のシークレット（例: `.streamlit/secrets.toml`）を利用します。

| キー | 用途 |
|------|------|
| **gemini** | Gemini API（api_key, model, max_retries, backoff_seconds） |
| **open_ai** | OpenAI API（api_key） |
| **google** | スプレッドシート・Drive 用（scout_folder_id, create_prompt_folder_id, scout_material_folder_id, jd_spreadsheet_id 等） |
| **gcp_service_account** / **gcp_service_account_jd** | GCP サービスアカウント情報（スプレッドシート・Drive 用） |
| **auth** | 認証（credentials, cookie の YAML） |

詳細は `config/settings.py` の各 `get_*_config()` を参照してください。

---

## 補足

- この README はツールの「叩き」ドキュメントです。運用が固まり次第、環境変数一覧・実行例・トラブルシュートなどを追記してください。
- スタンドアロンスクリプト（`batch_job.py`, `handle_structure_mapping.py` 等）の詳細なオプション・前提条件は、各ファイルのコメントや docstring を確認してください。
