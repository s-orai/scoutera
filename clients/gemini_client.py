from google import genai
from google.genai import types
import streamlit as st
from pydantic import BaseModel
from typing import List
import json
from contextlib import contextmanager

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

def request(content, temperature = 0.5):
  try:
    ## response_schemaの作成
    # PydanticモデルからJSONスキーマを取得
    response_schema = ResultsContainer.model_json_schema()

    print("🧠 Geminiモデルによる解析とスコアリングを開始します...")
    response = client.models.generate_content(
        model=model,
        contents=content,
        config=types.GenerateContentConfig(
            # JSON形式での出力を強制
            response_mime_type="application/json",
            response_schema = response_schema,
            temperature = temperature
        )
    )
    data = ResultsContainer.model_validate_json(response.text)
    return data.results

  except Exception as e:
      st.error(f"❌ Gemini APIの実行中にエラーが発生しました: {e}")
  except json.JSONDecodeError as e:
    print(f"JSON Parse Error: {str(e)}")
    print("Invalid JSON content:", data.results)
    raise

def multiple_requests(content, temperature = 0.5, try_times = n_trials):
  try:
    ## response_schemaの作成
    # PydanticモデルからJSONスキーマを取得
    response_schema = ResultsContainer.model_json_schema()

    results = []
    print("🧠 Geminiモデルによる解析とスコアリングを開始します...")
    for i in range(try_times):
      print(f"   - 試行 {i+1}回目")
      response = client.models.generate_content(
          model=model,
          contents=content,
          config=types.GenerateContentConfig(
              # JSON形式での出力を強制
              response_mime_type="application/json",
              response_schema = response_schema,
              temperature = temperature
          )
      )
      data = ResultsContainer.model_validate_json(response.text)
      results.append(data.results)

    return results

  except Exception as e:
      st.error(f"❌ Gemini APIの実行中にエラーが発生しました: {e}")
  except json.JSONDecodeError as e:
    print(f"JSON Parse Error: {str(e)}")
    print("Invalid JSON content:", results)
    raise

def request_with_files(prompt, files, temperature, try_times = n_trials):
  with file_uploader(files) as uploaded_files:

    content = [prompt] + uploaded_files
    results = multiple_requests(content, temperature, try_times)
  
  return results

@contextmanager
def file_uploader(files):
    """
    ファイルをGemini APIにアップロードし、ファイル名を 'with' ブロックに提供します。
    ブロック終了時に、成功・失敗に関わらず必ずファイルを削除します。
    """
    uploaded_file = None
    try:
      ## 1. Gemini APIへのファイルのアップロード
      temp_uploaded_files = []

      for path, original_name in files:
        uploaded_file = client.files.upload(file=path)
        temp_uploaded_files.append(uploaded_file)
        print(f"  アップロード: {original_name}")

      yield temp_uploaded_files

    except Exception as e:
        # アップロードまたは 'with' ブロック内の処理で例外が発生した場合
        print(f"Error during file processing: {e}")
        raise # 例外を呼び出し元に再スロー

    finally:
      ## 5. アップロードしたファイルの削除 (Gemini Filesから)
      if uploaded_file:
        print(f"🗑️ Gemini Filesからアップロードしたファイル ({uploaded_file.name}) を削除します。")
        client.files.delete(name=uploaded_file.name)
        print("✅ 削除完了。")