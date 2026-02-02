import streamlit as st
st.set_page_config(page_title="Scout Automation")

import streamlit_authenticator as stauth
import yaml
from services.scout import main as scout
from services.jd import main as jd

# secrets.toml から取得
config = {
    "credentials": yaml.safe_load(st.secrets["auth"]["credentials"])["credentials"],
    "cookie": yaml.safe_load(st.secrets["auth"]["cookie"])["cookie"],
}

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

# ----------------------------
# 初期化
# ----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "Scout"


def login():
    authenticator.login()
    if st.session_state["authentication_status"]:
        # 職種コンポーネントが正しく初期化されるように、ログイン成功したら一度リロードを挟む
        if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
            st.session_state["logged_in"] = True
            st.rerun() # これは不要になるかもしれない、後々確認して削除
        # ログイン後に別ファイルを描画
        # search.show_search_console()
    elif st.session_state["authentication_status"] is False:
        st.error("ユーザー名またはパスワードが間違っています")
    elif st.session_state["authentication_status"] is None:
        st.warning("ユーザー名とパスワードを入力してください")

def scout_page():
    st.title('Scout Automation')
    scout.show_search_console()

def jd_page():
    st.title('Jd Assist')
    jd.show_jd_create_console()

def logout_page():
    st.title("ログアウト")
    if st.button("ログアウトする"):
        st.session_state.logged_in = False
        st.session_state.page = "Home"
        st.rerun()

def main():
    # ログインしていない場合
    if st.session_state["logged_in"] is False:
        login()
        return

    # ログイン後のみサイドバー表示
    with st.sidebar:
        st.title("メニュー")
        st.session_state.page = st.radio(
            "ページ選択",
            ["Scout", "Jd", "Logout"]
        )

    # ページ切り替え
    if st.session_state.page == "Scout":
        scout_page()
    elif st.session_state.page == "Jd":
        jd_page()
    elif st.session_state.page == "Logout":
        logout_page()

if __name__ == "__main__":
    main()