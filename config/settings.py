"""
設定・シークレットの取得を集約する。
Streamlit の st.secrets を参照するのはこのモジュール内のみとし、
必要な key の不足や typo を一か所で把握できるようにする。
"""

import yaml

import streamlit as st


def get_gemini_config():
    """
    Gemini API 用の設定を返す。
    Returns:
        dict: api_key, model, max_retries, backoff_seconds
    """
    gemini = st.secrets["gemini"]
    return {
        "api_key": gemini["api_key"],
        "model": gemini.get("model", "gemini-3-pro-preview"),
        "max_retries": gemini.get("max_retries", 3),
        "backoff_seconds": gemini.get("backoff_seconds", 1.5),
    }


def get_openai_config():
    """
    OpenAI API 用の設定を返す。
    Returns:
        dict: api_key
    """
    open_ai = st.secrets["open_ai"]
    return {
        "api_key": open_ai["api_key"],
    }


def get_google_config():
    """
    Google（スプレッドシート・Drive・サービスアカウント）用の設定を返す。
    Returns:
        dict: scout_folder_id, create_prompt_folder_id, scout_material_folder_id,
              jd_spreadsheet_id, gcp_service_account, gcp_service_account_jd
    """
    google = st.secrets["google"]
    return {
        "scout_folder_id": google["scout_folder_id"],
        "create_prompt_folder_id": google["create_prompt_folder_id"],
        "scout_material_folder_id": google["scout_material_folder_id"],
        "jd_spreadsheet_id": google["jd_spreadsheet_id"],
        "gcp_service_account": st.secrets["gcp_service_account"],
        "gcp_service_account_jd": st.secrets["gcp_service_account_jd"],
    }


def get_auth_config():
    """
    認証（streamlit-authenticator）用の設定を返す。
    credentials と cookie は YAML として格納されている前提でパースする。
    Returns:
        dict: credentials（パース済み）, cookie（パース済み）
    """
    auth = st.secrets["auth"]
    return {
        "credentials": yaml.safe_load(auth["credentials"])["credentials"],
        "cookie": yaml.safe_load(auth["cookie"])["cookie"],
    }
