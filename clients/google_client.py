import datetime
import streamlit as st
import gspread
from gspread_dataframe import set_with_dataframe
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

class GoogleClient:

    SCOPES = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    FOLDER_ID = st.secrets["google"]["folder_id"]



    def __init__(self) -> None:
        # サービスアカウント認証
        self.credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=self.SCOPES
        )

        # Drive API クライアント作成
        self.drive_client = build("drive", "v3", credentials=self.credentials)

        # gspread 用クライアント
        self.gspread_client = gspread.authorize(self.credentials)

    def create_spreadsheet(self):

        # スプレッドシートを作成（共有ドライブのフォルダ内）
        title = "import_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_metadata = {
            "name": title,
            "mimeType": "application/vnd.google-apps.spreadsheet",
            "parents": [self.FOLDER_ID]
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
