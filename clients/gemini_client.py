from google import genai
from google.genai import types
import streamlit as st
from pydantic import BaseModel
from typing import List
import json
from contextlib import contextmanager
import time
import concurrent.futures

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

def request(pdf, job_pdf, config):
  try:
    job_pdf.append(pdf)
    response = client.models.generate_content(
        model=model,
        contents=job_pdf,
        config=config
    )
    result = ResultsContainer.model_validate_json(response.text)
    print(result)
    return result

  except Exception as e:
    print(f"❌ Gemini APIの実行中にエラーが発生しました: {e}")
    raise
  except json.JSONDecodeError as e:
    print(f"JSON Parse Error: {str(e)}")
    print("Invalid JSON content:", result)
    raise

def request_with_files_by_parallel(prompt, files, job_file, temperature):
  print("--- 並列処理開始 ---")
  start_time = time.time()

  ## response_schemaの作成
  # PydanticモデルからJSONスキーマを取得
  response_schema = ResultsContainer.model_json_schema()
  config = types.GenerateContentConfig(
    system_instruction=prompt,
    # JSON形式での出力を強制
    response_mime_type="application/json",
    response_schema = response_schema,
    temperature = temperature
  )

  with file_uploader(files, job_file) as (uploaded_files, uploaded_job_files):
    results = parallel_process_requests(uploaded_files, uploaded_job_files, config)

  end_time = time.time()
  print("--- 並列処理終了 ---")
  print(f"合計実行時間: {end_time - start_time:.2f}秒")
  print(f"results: {results}")
  return results

def parallel_process_requests(pdf_list, job_pdf_list, config):
    """
    PDFリストを受け取り、各PDFに対して3回ずつAPIリクエストを並列実行し、
    結果を一つのリストにまとめて返します。
    """
    # 全てのリクエストを格納するためのリスト
    all_requests = []

    # PDFごとに3回のリクエストの引数を作成
    for pdf_path in pdf_list:
        for i in range(1, 4):  # 1回目、2回目、3回目
            all_requests.append((pdf_path, i))

    MAX_WORKERS = 10

    results = []

    # ThreadPoolExecutorを使用してタスクを並列実行
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # executor.submit() でタスクをキューに追加し、Futureオブジェクトを取得
        future_to_request = {
            executor.submit(request, pdf_path, job_pdf_list, config):
            (pdf_path, attempt_num)
            for pdf_path, attempt_num in all_requests
        }

        # concurrent.futures.as_completed() で完了した順に結果を取得
        for future in concurrent.futures.as_completed(future_to_request):
            pdf_path, attempt_num = future_to_request[future]

            try:
                # future.result() で実行結果を取得
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f"PDF: {pdf_path}, 試行: {attempt_num} の実行中に例外が発生しました: {exc}")

    return results

@contextmanager
def file_uploader(files, job_file):
    """
    ファイルをGemini APIにアップロードし、ファイル名を 'with' ブロックに提供します。
    ブロック終了時に、成功・失敗に関わらず必ずファイルを削除します。
    """
    uploaded_file = None
    try:
      temp_uploaded_files = []
      for path, original_name in files:
        uploaded_file = client.files.upload(file=path)
        temp_uploaded_files.append(uploaded_file)
        print(f"  アップロード: {original_name}")

      temp_uploaded_job_files = []
      for path, original_name in job_file:
        uploaded_job_file = client.files.upload(file=path)
        temp_uploaded_job_files.append(uploaded_job_file)
        print(f"  求人票アップロード: {original_name}")

      yield (temp_uploaded_files, temp_uploaded_job_files)

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