import datetime
import streamlit as st
import gspread
from gspread_dataframe import set_with_dataframe
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaIoBaseDownload
import os

class GoogleClient:

    SCOPES = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    jd_spreadsheet_id = st.secrets["google"]["jd_spreadsheet_id"]

    def __init__(self) -> None:
        # サービスアカウント認証
        self.credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=self.SCOPES
        )

        # Drive API クライアント作成
        self.drive_client = build("drive", "v3", credentials=self.credentials)

        # gspread 用クライアント
        self.gspread_client = gspread.authorize(self.credentials)

        # jd用サービスアカウント認証
        self.jd_credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account_jd"], scopes=self.SCOPES
        )

        # jd用Drive API クライアント作成
        self.jd_drive_client = build("drive", "v3", credentials=self.jd_credentials)

        # jd用gspread 用クライアント
        self.jd_gspread_client = gspread.authorize(self.jd_credentials)

    def create_spreadsheet(self, folder_id):

        # スプレッドシートを作成（共有ドライブのフォルダ内）
        title = "import_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_metadata = {
            "name": title,
            "mimeType": "application/vnd.google-apps.spreadsheet",
            "parents": [folder_id]
        }

        spreadsheet = self.drive_client.files().create(
            body=file_metadata,
            supportsAllDrives=True,
            fields="id"
        ).execute()

        spreadsheet_id = spreadsheet.get("id")
        print(f"✅ 新規スプレッドシート作成: {spreadsheet_id}")

        return spreadsheet_id

    def write_data(self, spreadsheet_id, df):

        # gspreadでシートを開く
        sheet = self.gspread_client.open_by_key(spreadsheet_id).sheet1

        # dfをシートに書き込み
        set_with_dataframe(sheet, df)

        # URLを組み立てる
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"

        print("✅ CSVをスプレッドシートにインポートしました！")
        return spreadsheet_url

    def download_audio_from_drive(self, file_id: str, output_path: str):
        info = self.jd_drive_client.files().get(
            fileId=file_id,
            fields="name, size, mimeType",
            supportsAllDrives=True
        ).execute()

        if not info["mimeType"].startswith("audio/"):
          raise ValueError("音声ファイルのみ対応しています")

        if int(info["size"]) > 100 * 1024 * 1024:
          raise ValueError("ファイルサイズが大きすぎます（100MB以内）")

        request = self.jd_drive_client.files().get_media(
          fileId=file_id,
          supportsAllDrives=True
        )
        with open(output_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

        ## 正常にダウンロードできているかチェック
        ## この数字が少ないと、正常にダウンロードできていない証拠
        print("size:", os.path.getsize(output_path))

    def get_job_description_from_spreadsheet(self):
        """
        Googleスプレッドシートから職種と仕事内容のマッピングを取得する
        
        Args:
            spreadsheet_id: スプレッドシートのID
            sheet_name: シート名（指定しない場合は最初のシート）
        
        Returns:
            dict: 職種をキー、仕事内容を値とする辞書
        """
        try:
            # スプレッドシートを開く
            spreadsheet = self.jd_gspread_client.open_by_key(self.jd_spreadsheet_id)
            sheet = spreadsheet.sheet1
            
            # すべてのデータを取得
            all_values = sheet.get_all_values()
            
            if not all_values or len(all_values) < 2:
                print("⚠️ スプレッドシートにデータが存在しません")
                return {}
            
            # ヘッダー行を除いてデータを辞書に変換
            # 1列目：index, ２列目：分類, 3列目：職種、4列目：仕事内容
            job_mapping = {}
            for row in all_values[1:]:  # ヘッダーをスキップ
                if len(row) >= 4 and row[2]:  # 職種が存在する場合
                    job_category = row[2].strip()
                    job_description = row[3].strip() if len(row) > 3 else ""
                    job_mapping[job_category] = job_description
            
            print(f"✅ スプレッドシートから{len(job_mapping)}件の職種マッピングを取得しました")
            return job_mapping
            
        except Exception as e:
            print(f"❌ スプレッドシートからのデータ取得中にエラーが発生しました: {e}")
            raise
