from google.genai import types
import streamlit as st
from google import genai
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
# リトライ回数上限
max_retries = 3
# リトライ時のAPI問い合わせ間隔
backoff_seconds = 1.5

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

class CreatePromptModel(BaseModel):
  common_skill_of_A: str
  difference_of_ab_and_c: str
  difference_of_a_and_b: str
  required_condition: str
  welcome_condition: str

class ScoutMaterialModel(BaseModel):
  persona: str
  category: str
  industry: str
  keyword: str
  income: str
  desired_income: str
  scout_title: str
  scout_body: str

def request_for_create_prompt(prompt, files, job_file, temperature):
  print("--- 処理開始 ---")
  start_time = time.time()

  ## response_schemaの作成
  # PydanticモデルからJSONスキーマを取得
  response_schema = CreatePromptModel.model_json_schema()
  config = types.GenerateContentConfig(
    system_instruction=prompt,
    # JSON形式での出力を強制
    response_mime_type="application/json",
    response_schema = response_schema,
    temperature = temperature
  )

  with file_uploader(files, job_file) as (uploaded_files, uploaded_job_files):
    response = request(uploaded_files, uploaded_job_files, config)
    result = CreatePromptModel.model_validate_json(response.text)
    print(result)

  end_time = time.time()
  print("--- 並列処理終了 ---")
  print(f"合計実行時間: {end_time - start_time:.2f}秒")
  print(f"result: {result}")
  return result

def request(pdf, job_pdfs, config):
  for attempt in range(1, max_retries + 1):
    try:
      # API呼び出し
      contents = [pdf] + list(job_pdfs)
      response = client.models.generate_content(
          model=model,
          contents=contents,
          config=config
      )
      return response

    except json.JSONDecodeError as e:
      # JSONパースエラーはリトライしても解決しないため、即座に例外を再発生
      print(f"JSON Parse Error: {str(e)}")
      print("Invalid JSON content:", response.text if 'response' in locals() else '')
      raise

    except Exception as e:
      # 最後の試行の場合は例外を再発生
      if attempt == max_retries:
        print(f"❌ Gemini APIの実行中にエラーが発生しました (attempt {attempt}/{max_retries}): {e}")
        raise

      print(f"⚠️ Gemini APIエラー (attempt {attempt}/{max_retries}): {e} - {backoff_seconds}秒待機後にリトライします")
      time.sleep(backoff_seconds)
      # ループが継続され、次の試行が実行される

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
    all_requests = [
        (pdf_path, attempt_num)
        for pdf_path in pdf_list
        for attempt_num in range(1, 4)
    ]

    MAX_WORKERS = 10
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_request = {
            executor.submit(request, pdf_path, job_pdf_list, config):
            (pdf_path, attempt_num)
            for pdf_path, attempt_num in all_requests
        }

        for future in concurrent.futures.as_completed(future_to_request):
            pdf_path, attempt_num = future_to_request[future]
            try:
                response = future.result()
                result = ResultsContainer.model_validate_json(response.text)
                print(result)
                results.append(result)
            except Exception as exc:
                print(f"PDF: {pdf_path}, 試行: {attempt_num} の実行中に例外が発生しました: {exc}")

    return results

def request_with_files_for_scout_material(prompt, files, temperature):
  print("--- 処理開始 ---")
  start_time = time.time()

  ## response_schemaの作成
  # PydanticモデルからJSONスキーマを取得
  response_schema = ScoutMaterialModel.model_json_schema()
  config = types.GenerateContentConfig(
    system_instruction=prompt,
    # JSON形式での出力を強制
    response_mime_type="application/json",
    response_schema = response_schema,
    temperature = temperature
  )

  with _file_uploader(files) as uploaded_files:
    response = _request(uploaded_files, config)

  end_time = time.time()
  print(f"合計実行時間: {end_time - start_time:.2f}秒")
  # レスポンスをパースしてモデルを返す（logic側でtuple/listと勘違いしないように）
  result = ScoutMaterialModel.model_validate_json(response.text)
  print(f"result: {result}")
  return result

# ----------------------------
# ここからはjd用
# ＊後で統合すること！！
# ----------------------------
class OfferingContentModel(BaseModel):
  background: str
  job_category: str
  required_requirement: str
  welcome_requirement: str
  character_statue: str

class BussinessDescriptionModel(BaseModel):
  company_name: str
  business_service_name: str
  company_philosophy: str
  business_introduction: str
  business_detail: str

def request_business_description(prompt, temperature):
  print("--- 処理開始 ---")
  start_time = time.time()

  ## response_schemaの作成
  # PydanticモデルからJSONスキーマを取得
  response_schema = BussinessDescriptionModel.model_json_schema()
  config = types.GenerateContentConfig(
    # JSON形式での出力を強制
    response_mime_type="application/json",
    response_schema = response_schema,
    temperature = temperature
  )

  response = _request_only_config(config, prompt)
  result = BussinessDescriptionModel.model_validate_json(response.text)

  end_time = time.time()
  print(f"合計実行時間: {end_time - start_time:.2f}秒")
  return result

def request_with_files_for_jd(prompt, files, temperature):
  print("--- 処理開始 ---")
  start_time = time.time()

  ## response_schemaの作成
  # PydanticモデルからJSONスキーマを取得
  response_schema = OfferingContentModel.model_json_schema()
  config = types.GenerateContentConfig(
    system_instruction=prompt,
    # JSON形式での出力を強制
    response_mime_type="application/json",
    response_schema = response_schema,
    temperature = temperature
  )

  with _file_uploader(files) as uploaded_files:
    response = _request(uploaded_files, config)

  end_time = time.time()
  print(f"合計実行時間: {end_time - start_time:.2f}秒")
  # レスポンスをパースしてモデルを返す（logic側でtuple/listと勘違いしないように）
  result = OfferingContentModel.model_validate_json(response.text)
  print(f"result: {result}")
  return result

def _request_only_config(config, prompt):
  for attempt in range(1, max_retries + 1):
    try:
      # API呼び出し
      response = client.models.generate_content(
          model=model,
          config=config,
          contents=[prompt]
      )
      return response

    except json.JSONDecodeError as e:
      # JSONパースエラーはリトライしても解決しないため、即座に例外を再発生
      print(f"JSON Parse Error: {str(e)}")
      print("Invalid JSON content:", response.text if 'response' in locals() else '')
      raise

    except Exception as e:
      # 最後の試行の場合は例外を再発生
      if attempt == max_retries:
        print(f"❌ Gemini APIの実行中にエラーが発生しました (attempt {attempt}/{max_retries}): {e}")
        raise

      print(f"⚠️ Gemini APIエラー (attempt {attempt}/{max_retries}): {e} - {backoff_seconds}秒待機後にリトライします")
      time.sleep(backoff_seconds)
      # ループが継続され、次の試行が実行される

def _request(pdfs, config):
  for attempt in range(1, max_retries + 1):
    try:
      # API呼び出し
      contents = pdfs
      response = client.models.generate_content(
          model=model,
          contents=contents,
          config=config
      )
      return response

    except json.JSONDecodeError as e:
      # JSONパースエラーはリトライしても解決しないため、即座に例外を再発生
      print(f"JSON Parse Error: {str(e)}")
      print("Invalid JSON content:", response.text if 'response' in locals() else '')
      raise

    except Exception as e:
      # 最後の試行の場合は例外を再発生
      if attempt == max_retries:
        print(f"❌ Gemini APIの実行中にエラーが発生しました (attempt {attempt}/{max_retries}): {e}")
        raise

      print(f"⚠️ Gemini APIエラー (attempt {attempt}/{max_retries}): {e} - {backoff_seconds}秒待機後にリトライします")
      time.sleep(backoff_seconds)
      # ループが継続され、次の試行が実行される

# ----------------------------
# 共通関数
# ----------------------------
@contextmanager
def file_uploader(files, job_file, is_round: bool = False):
    """
    ファイルをGemini APIにアップロードし、ファイル名を 'with' ブロックに提供します。
    ブロック終了時に、成功・失敗に関わらず必ずファイルを削除します。
    """
    uploaded_files = []
    uploaded_job_files = []
    try:
      for path, original_name in files:
        uploaded = client.files.upload(file=path)
        uploaded_files.append(uploaded)
        print(f"  アップロード: {original_name}")

      for path, original_name in job_file:
        uploaded = client.files.upload(file=path)
        uploaded_job_files.append(uploaded)
        print(f"  求人票アップロード: {original_name}")

      if not is_round:
        yield (uploaded_files, uploaded_job_files)
      else:
        uploaded_files.extend(uploaded_job_files)
        yield uploaded_files

    except Exception as e:
        # アップロードまたは 'with' ブロック内の処理で例外が発生した場合
        print(f"Error during file processing: {e}")
        raise # 例外を呼び出し元に再スロー

    finally:
      ## 5. アップロードしたファイルの削除 (Gemini Filesから)
      for uploaded in uploaded_files + uploaded_job_files:
        try:
          print(f"🗑️ Gemini Filesからアップロードしたファイル ({uploaded.name}) を削除します。")
          client.files.delete(name=uploaded.name)
          print("✅ 削除完了。")
        except Exception as delete_error:
          print(f"⚠️ ファイル削除に失敗しました: {delete_error}")

@contextmanager
def _file_uploader(files):
    """
    ファイルをGemini APIにアップロードし、ファイル名を 'with' ブロックに提供します。
    ブロック終了時に、成功・失敗に関わらず必ずファイルを削除します。
    """
    uploaded_files = []
    try:
      for path, original_name in files:
        uploaded = client.files.upload(file=path)
        uploaded_files.append(uploaded)
        print(f"  アップロード: {original_name}")

      # 1ファイルの場合は単体で、複数の場合はリストで渡す
      if len(uploaded_files) == 1:
        yield uploaded_files[0]
      else:
        yield uploaded_files

    except Exception as e:
        # アップロードまたは 'with' ブロック内の処理で例外が発生した場合
        print(f"Error during file processing: {e}")
        raise # 例外を呼び出し元に再スロー

    finally:
      ## 5. アップロードしたファイルの削除 (Gemini Filesから)
      for uploaded in uploaded_files:
        try:
          print(f"🗑️ Gemini Filesからアップロードしたファイル ({uploaded.name}) を削除します。")
          client.files.delete(name=uploaded.name)
          print("✅ 削除完了。")
        except Exception as delete_error:
          print(f"⚠️ ファイル削除に失敗しました: {delete_error}")