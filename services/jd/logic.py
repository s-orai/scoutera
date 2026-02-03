import streamlit as st
from clients import google_client
from clients import gemini_client
from clients import openai_client
from services.jd import preparation_ai
import tempfile
import re
import ffmpeg
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

scout_folder_id = st.secrets["google"]["scout_folder_id"]
create_prompt_folder_id = st.secrets["google"]["create_prompt_folder_id"]
jd_spreadsheet_id = st.secrets["google"]["jd_spreadsheet_id"]

google_cli = google_client.GoogleClient()
openai_cli = openai_client.OpenAIClient()


def create_business_description(url, temperature):
  company_info = preparation_ai.scrape_page_text(url)
  prompt = preparation_ai.format_prompt_for_business_description(company_info)
  result = gemini_client.request_business_description(prompt, temperature)
  data_dicts = result.model_dump()
  df = pd.DataFrame([data_dicts])

  return df.iloc[0]

def create_business_description_chatgpt(company_info, temperature):
  prompt = preparation_ai.format_prompt_for_business_description(company_info)
  result = openai_cli.chat(prompt, temperature)
  # 余分な文字列を削除
  cleaned_res = result.replace('```json', '').replace('```', '').strip()
  parsed_json = json.loads(cleaned_res)
  df = pd.DataFrame([parsed_json])

  return df.iloc[0]


def create_jd(company_info, video_link, jd_pdf, temperature):
  file_id = _extract_file_id(video_link)
  audio_text = _audio_transcription(file_id)

  for _, original_name in jd_pdf:
    jd_title = original_name

  prompt = preparation_ai.format_prompt_for_jd(company_info, audio_text, jd_title)

  result = gemini_client.request_with_files_for_jd(prompt, jd_pdf, temperature)
  data_dicts = result.model_dump()
  df = pd.DataFrame([data_dicts])
  df = _enrich_jd_with_job_description(df)

  return df.iloc[0]

def _enrich_jd_with_job_description(df):
  """
  データフレームから募集職種を抽出し、スプレッドシートから仕事内容を取得して追加する

  Args:
      df: 募集情報を含むDataFrame（job_categoryカラムを持つ）

  Returns:
      DataFrame: job_descriptionカラムが追加されたDataFrame
  """
  try:
    # スプレッドシートから職種マッピングを取得
    job_mapping = google_cli.get_job_description_from_spreadsheet()
    
    # データフレームのコピーを作成
    enriched_df = df.copy()
    
    # 募集職種を抽出して仕事内容をマッピング
    if 'job_category' in enriched_df.columns:
      enriched_df['job_content'] = enriched_df['job_category'].apply(
        lambda x: job_mapping.get(x, "該当する職種の仕事内容が見つかりませんでした")
      )
      print(f"✅ {len(enriched_df)}件の募集職種に仕事内容を追加しました")
    else:
      print("⚠️ データフレームに'job_category'カラムが存在しません")
      enriched_df['job_content'] = ""
    
    return enriched_df
  except Exception as e:
    print(f"⚠️ スプレッドシートからの取得中にエラーが発生しました: {e}")
    print("仕事内容の追加をスキップします")
    return df


def _audio_transcription(file_id):
  try:
    with tempfile.TemporaryDirectory() as tmpdir:
      tmp = Path(tmpdir)

      input_m4a = tmp / "input.m4a"
      input_wav = tmp / "input.wav"
      segments_dir = tmp / "segments"
      cache_dir = tmp / "cache"

      # ① DriveからDL
      google_cli.download_audio_from_drive(
        file_id =file_id,
        output_path=str(input_m4a)
        )

      # ② m4a → wav
      _convert_to_wav(
          input_path=str(input_m4a),
          output_path=str(input_wav),
      )

      # ③ wav 分割
      _split_wav(
          input_path=str(input_wav),
          segment_dir=str(segments_dir),
          sec=300,
      )
      segments = sorted(Path(segments_dir).glob("seg_*.wav"))
      print(f"[INFO] audio split into {len(segments)} segments")

      # ④ 書き起こし
      results = _transcribe_all(
          segments=segments,
          cache_dir=str(cache_dir),
          openai_cli=openai_cli,
      )

      # ⑤ 結合
      return _merge_text(results)

  except Exception as e:
        st.error(f"エラーが発生しました: {e}")

## 動画リンクから、fileIDを抜き取る
def _extract_file_id(drive_url: str) -> str:
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", drive_url)
    if not match:
        raise ValueError("Invalid Google Drive URL")
    return match.group(1)

def _convert_to_wav(
    input_path: str,
    output_path: str
  ):
    """
    音声ファイルを OpenAI Whisper 向けの WAV に変換する
    """
    try:
      (
        ffmpeg
        .input(input_path)
        .output(
            output_path,
            ac=1,
            ar=16000,
            format="wav"
        )
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
      )
    except ffmpeg.Error as e:
        print("ffmpeg stdout:")
        print(e.stdout.decode("utf-8", errors="ignore"))
        print("ffmpeg stderr:")
        print(e.stderr.decode("utf-8", errors="ignore"))
        raise

def _split_wav(
    input_path: str,
    segment_dir: str,
    sec: int = 300,
):
    Path(segment_dir).mkdir(exist_ok=True)

    (
        ffmpeg
        .input(input_path)
        .output(
            f"{segment_dir}/seg_%03d.wav",
            f="segment",
            segment_time=sec,
            reset_timestamps=1,
        )
        .run(quiet=True)
    )

import json
from pathlib import Path

def _transcribe_with_cache(
    index: int,
    audio_path: str,
    cache_dir: str,
    openai_cli,
):
    cache_path = Path(cache_dir) / f"seg_{index:03d}.json"

    if cache_path.exists():
        print(f"[CACHE] segment {index} hit")
        with open(cache_path) as f:
            return json.load(f)

    text = openai_cli.transcribe_audio(audio_path)

    data = {
        "index": index,
        "text": text,
    }

    with open(cache_path, "w") as f:
        json.dump(data, f, ensure_ascii=False)

    return data

def _transcribe_all(
    segments: list[Path],
    cache_dir: str,
    openai_cli,
    max_workers: int = 3,
):
    Path(cache_dir).mkdir(exist_ok=True)
    total = len(segments)

    print(f"[INFO] start transcription: {total} segments")
    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _transcribe_with_cache,
                i,
                str(path),
                cache_dir,
                openai_cli,
            ): i
            for i, path in enumerate(segments)
        }

        completed = 0
        for future in as_completed(futures):
            i = futures[future]
            try:
              data = future.result()
              results[data["index"]] = data["text"]
              completed += 1
              print(
                      f"[INFO] transcribed {completed}/{total} "
                      f"(segment {i})"
                  )
            except Exception as e:
                print(f"[ERROR] segment {i} failed: {e}")
                raise

    return results

def _merge_text(results: dict) -> str:
    return "\n".join(
        results[i] for i in sorted(results)
    )
