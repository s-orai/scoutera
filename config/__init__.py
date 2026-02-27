"""
設定・シークレットの取得を集約するモジュール。
各クライアント・サービスは st.secrets を直接参照せず、ここ経由で取得する。
"""

from config.settings import (
    get_auth_config,
    get_gemini_config,
    get_google_config,
    get_openai_config,
)

__all__ = [
    "get_auth_config",
    "get_gemini_config",
    "get_google_config",
    "get_openai_config",
]
