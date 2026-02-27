from google.genai import types
from google import genai
import json
from contextlib import contextmanager
import time
import concurrent.futures

from config import get_gemini_config
# モデルのインポート
from models.scout_models import (
    AiResult,
    ResultsContainer,
    CreatePromptModel,
    ScoutMaterialModel
)
from models.jd_models import (
    OfferingContentModel,
    BussinessDescriptionModel
)
from models.screening_models import (
    ScreeningResult,
)
# モデルを外部からアクセス可能にする
__all__ = [
    # Functions
    "request_for_create_prompt",
    "request_with_files_by_parallel",
    "request_with_files_for_scout_material",
    "request_business_description",
    "request_with_files_for_jd",
    # Models (backward compatibility)
    "AiResult",
    "ResultsContainer",
    "CreatePromptModel",
    "ScoutMaterialModel",
    "OfferingContentModel",
    "BussinessDescriptionModel",
    "ScreeningResult",
]

_gemini_config = get_gemini_config()
api_key = _gemini_config["api_key"]
model = _gemini_config["model"]
max_retries = _gemini_config["max_retries"]
backoff_seconds = _gemini_config["backoff_seconds"]

client = genai.Client(api_key=api_key)
n_trials = 3


def _execute_with_retry(api_call):
  """
  リトライ・バックオフ・例外処理を共通化したAPI実行ヘルパー。
  api_call は引数なしで呼ばれ、1回分の generate_content のレスポンスを返す callable を渡す。
  """
  for attempt in range(1, max_retries + 1):
    try:
      response = api_call()
      return response
    except json.JSONDecodeError as e:
      print(f"JSON Parse Error: {str(e)}")
      print("Invalid JSON content:", response.text if 'response' in locals() else '')
      raise
    except Exception as e:
      if attempt == max_retries:
        print(f"❌ Gemini APIの実行中にエラーが発生しました (attempt {attempt}/{max_retries}): {e}")
        raise
      print(f"⚠️ Gemini APIエラー (attempt {attempt}/{max_retries}): {e} - {backoff_seconds}秒待機後にリトライします")
      time.sleep(backoff_seconds)


def request_for_create_prompt(prompt, files, job_file, temperature=0.2):
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

def request(pdfs, job_pdfs, config):
  def _call():
    if isinstance(pdfs, list):
      contents = pdfs + list(job_pdfs)
    else:
      contents = [pdfs] + list(job_pdfs)
    return client.models.generate_content(
        model=model,
        contents=contents,
        config=config
    )
  return _execute_with_retry(_call)

def request_with_files_by_parallel(prompt, files, job_file, response_model, temperature=0.2, is_screening=False):
  """
  PDFファイルに対してGemini APIリクエストを並列実行する
  
  Args:
      prompt: システムプロンプト
      files: 候補者PDFファイルのリスト
      job_file: 求人票PDFファイル
      response_model: レスポンスのPydanticモデル
      temperature: 温度パラメータ
      is_screening: Trueの場合はscreeningモード（全体を3回実行）、Falseの場合はscoutモード（各PDFを3回ずつ実行）
  
  Returns:
      処理結果のリスト
  """
  print("--- 並列処理開始 ---")
  start_time = time.time()

  ## response_schemaの作成
  # PydanticモデルからJSONスキーマを取得
  response_schema = response_model.model_json_schema()
  config = types.GenerateContentConfig(
    system_instruction=prompt,
    # JSON形式での出力を強制
    response_mime_type="application/json",
    response_schema = response_schema,
    temperature = temperature
  )

  with file_uploader(files, job_file) as (uploaded_files, uploaded_job_files):
    if is_screening:
      results = _parallel_process_for_screening(uploaded_files, uploaded_job_files, config, response_model)
    else:
      results = _parallel_process_for_scout(uploaded_files, uploaded_job_files, config, response_model)

  end_time = time.time()
  print("--- 並列処理終了 ---")
  print(f"合計実行時間: {end_time - start_time:.2f}秒")
  print(f"results: {results}")
  return results

def _parallel_process_for_scout(pdf_list, job_pdf_list, config, response_model):
    """
    Scout用: PDFリストを受け取り、各PDFに対して3回ずつAPIリクエストを並列実行し、
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
            executor.submit(request, pdf_path, job_pdf_list, config): (pdf_path, attempt_num)
            for pdf_path, attempt_num in all_requests
        }

        for future in concurrent.futures.as_completed(future_to_request):
            pdf_path, attempt_num = future_to_request[future]
            try:
                response = future.result()
                result = response_model.model_validate_json(response.text)
                print(result)
                results.append(result)
            except Exception as exc:
                print(f"PDF: {pdf_path}, 試行: {attempt_num} の実行中に例外が発生しました: {exc}")

    return results

def _parallel_process_for_screening(pdf_list, job_pdf, config, response_model):
    """
    Screening用: PDFリスト全体に対して3回APIリクエストを並列実行し、
    結果を一つのリストにまとめて返します。
    
    Args:
        pdf_list: 候補者PDFのリスト
        job_pdf: 求人票PDFのリスト
        config: API設定
        response_model: レスポンスモデル
    
    Returns:
        List[response_model]: 3回の実行結果のリスト
    """
    MAX_WORKERS = 10
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # PDFリスト全体を3回実行
        futures = [
            executor.submit(request, pdf_list, job_pdf, config)
            for _ in range(3)
        ]

        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            try:
                response = future.result()
                result = response_model.model_validate_json(response.text)
                print(f"✅ 実行 {i}/3 完了")
                print(result)
                results.append(result)
            except Exception as exc:
                print(f"❌ 実行 {i}/3 で例外が発生しました: {exc}")

    return results

def request_with_files_for_scout_material(prompt, files, temperature=0.2):
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

  with file_uploader(files, []) as (uploaded_files, _):
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

  with file_uploader(files, []) as (uploaded_files, _):
    response = _request(uploaded_files, config)

  end_time = time.time()
  print(f"合計実行時間: {end_time - start_time:.2f}秒")
  # レスポンスをパースしてモデルを返す（logic側でtuple/listと勘違いしないように）
  result = OfferingContentModel.model_validate_json(response.text)
  print(f"result: {result}")
  return result

def _request_only_config(config, prompt):
  return _execute_with_retry(
      lambda: client.models.generate_content(
          model=model,
          config=config,
          contents=[prompt]
      )
  )

def _request(pdfs, config):
  return _execute_with_retry(
      lambda: client.models.generate_content(
          model=model,
          contents=pdfs,
          config=config
      )
  )
# ----------------------------
# 共通関数（ファイルアップロード）
# ----------------------------
@contextmanager
def file_uploader(files, job_file=None, is_round: bool = False):
    """
    ファイルをGemini APIにアップロードし、'with' ブロックに (uploaded_files, uploaded_job_files) を提供します。
    ブロック終了時に、成功・失敗に関わらず必ずアップロードしたファイルを削除します。

    Args:
        files: [(ローカルパス, オリジナルファイル名), ...] のリスト（候補者用など）
        job_file: 求人票用の [(パス, 名前), ...]。省略時は空リストとして扱う（候補者のみアップロード）
        is_round: True のときは (uploaded_files + uploaded_job_files) を1つのリストで yield
    """
    job_file = job_file if job_file is not None else []
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
        print(f"Error during file processing: {e}")
        raise

    finally:
      for uploaded in uploaded_files + uploaded_job_files:
        try:
          print(f"🗑️ Gemini Filesからアップロードしたファイル ({uploaded.name}) を削除します。")
          client.files.delete(name=uploaded.name)
          print("✅ 削除完了。")
        except Exception as delete_error:
          print(f"⚠️ ファイル削除に失敗しました: {delete_error}")