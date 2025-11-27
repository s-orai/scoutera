from google import genai
from google.genai import types
import streamlit as st



api_key = st.secrets["gemini"]["api_key"]
model = "gemini-2.5-flash"
client = genai.Client(api_key=api_key)

# def __init__(self) -> None:
#   self.client = genai.Client(api_key=self.api_key)

def call_api(pdfs, prompt):
    """
    一時的に保存されたPDFファイルをGemini APIで解析し、スコアリングを行う関数。
    """
    uploaded_file = None
    print("アップロード開始")
    try:
        ## 1. Gemini APIへのファイルのアップロード
        temp_uploaded_files = []
        for path, original_name in pdfs:
          uploaded_file = client.files.upload(file=path)
          temp_uploaded_files.append(uploaded_file)
          print(f"  アップロード: {original_name}")

        uploaded_files = temp_uploaded_files # 成功したファイルリストを保持
        print(f"✅ Gemini Filesへのアップロードが完了しました。URI: {uploaded_file.uri}")
     
        ## 2. モデルへの入力を作成
        contents = [prompt] + uploaded_files

        ## 3. モデルの呼び出し（Gemini 2.5 Proを使用）
        print("🧠 Geminiモデルによる解析とスコアリングを開始します...")
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                # JSON形式での出力を強制
                response_mime_type="application/json", 
            )
        )
        return response
    except Exception as e:
        st.error(f"❌ Gemini APIの実行中にエラーが発生しました: {e}")
    finally:
        ## 5. アップロードしたファイルの削除 (Gemini Filesから)
        if uploaded_file:
            print(f"🗑️ Gemini Filesからアップロードしたファイル ({uploaded_file.name}) を削除します。")
            client.files.delete(name=uploaded_file.name)
            print("✅ 削除完了。")