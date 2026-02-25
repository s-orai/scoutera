"""
Streamlit UI 用の共通ユーティリティ。
スタイル注入や、見出し＋コードブロックの表示パターンをまとめる。
"""

from typing import Optional

import streamlit as st


def inject_code_block_style() -> None:
    """
    pre/code ブロックの折り返し・改行用スタイルを注入する。
    長いテキストがコードブロックで見切れないようにする。
    結果表示を行う画面で1回呼び出す。
    """
    st.markdown(
        """
        <style>
        pre code {
            white-space: pre-wrap !important;
            word-break: break-word !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_code_sections(
    sections: dict[str, str],
    main_title: Optional[str] = None,
) -> None:
    """
    見出し＋区切り＋コードブロックのパターンで複数セクションを表示する。

    Args:
        sections: セクション名 → 表示するテキスト の辞書（表示順は挿入順）
        main_title: 省略可。指定時はその上に st.header で大見出しを表示する。

    Examples:
        show_code_sections(
            {"募集背景": res["background"], "募集職種": res["job_category"]},
            main_title="作成した募集要項"
        )
    """
    if main_title is not None:
        st.header(main_title)
    for label, content in sections.items():
        st.subheader(label, divider=True)
        st.code(str(content), language=None)
