from google import genai
from google.genai import types
import streamlit as st
from pydantic import BaseModel
from typing import List
import json

api_key = st.secrets["gemini"]["api_key"]
model = "gemini-3-pro-preview"
client = genai.Client(api_key=api_key)
n_trials = 3

# def __init__(self) -> None:
#   self.client = genai.Client(api_key=self.api_key)

class AiResult(BaseModel):
  """
  AIの結果を格納するモデル
  """
  id: str
  required_condition: bool
  welcome_condition: bool
  evaluation_reason: str
  evaluation_result: str
  scout_message: str


class ResultsContainer(BaseModel):
  """結果全体を格納するコンテナ"""
  results: List[AiResult]

def call_api(pdfs, job_pdfs, prompt, temperature):
    """
    一時的に保存されたPDFファイルをGemini APIで解析し、スコアリングを行う関数。
    """
    uploaded_file = None
    print("アップロード開始")
    try:
        ## 1. Gemini APIへのファイルのアップロード
        temp_uploaded_files = []

        for path, original_name in job_pdfs:
          uploaded_file = client.files.upload(file=path)
          temp_uploaded_files.append(uploaded_file)
          print(f"  アップロード: {original_name}")

        for path, original_name in pdfs:
          uploaded_file = client.files.upload(file=path)
          temp_uploaded_files.append(uploaded_file)
          print(f"  アップロード: {original_name}")

        uploaded_files = temp_uploaded_files # 成功したファイルリストを保持
     
        ## 2. モデルへの入力を作成
        contents = [prompt] + uploaded_files

        ## response_schemaの作成
        # PydanticモデルからJSONスキーマを取得
        response_schema = ResultsContainer.model_json_schema()

        ## 3. モデルの呼び出し（Gemini 2.5 Proを使用）
        results = []
        print("🧠 Geminiモデルによる解析とスコアリングを開始します...")
        for i in range(n_trials):
          response = client.models.generate_content(
              model=model,
              contents=contents,
              config=types.GenerateContentConfig(
                  # JSON形式での出力を強制
                  response_mime_type="application/json",
                  response_schema = response_schema,
                  temperature = temperature
              )
          )
          data = ResultsContainer.model_validate_json(response.text)
          results.append(data.results)
          print(f"   - 試行 {i+1}: {data.results}")

        return results

    except Exception as e:
      st.error(f"❌ Gemini APIの実行中にエラーが発生しました: {e}")
    except json.JSONDecodeError as e:
      print(f"JSON Parse Error: {str(e)}")
      print("Invalid JSON content:", results)
      raise
    finally:
        ## 5. アップロードしたファイルの削除 (Gemini Filesから)
        if uploaded_file:
            print(f"🗑️ Gemini Filesからアップロードしたファイル ({uploaded_file.name}) を削除します。")
            client.files.delete(name=uploaded_file.name)
            print("✅ 削除完了。")