"""
Web/HTTP系の共通ユーティリティ
"""

import re

import requests
from bs4 import BeautifulSoup


def scrape_page_text(url: str, timeout: int = 10) -> str:
    """
    URLからHTMLを取得し、求人要約向けに本文テキストだけを抽出して返す
    Gemini / OpenAI 共通で使用可能
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    res = requests.get(url, headers=headers, timeout=timeout)
    res.raise_for_status()

    # 文字コード対策
    res.encoding = res.apparent_encoding

    soup = BeautifulSoup(res.text, "html.parser")

    # 不要要素を削除
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()

    # body からテキスト抽出
    text = soup.get_text(separator="\n")

    # 後処理（空行・ノイズ削除）
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if len(line) < 5:  # 短すぎるノイズ除外
            continue
        lines.append(line)

    cleaned_text = "\n".join(lines)

    # 連続改行を整理
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    return cleaned_text

