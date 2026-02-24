"""
共通ユーティリティ関数
"""

import tempfile


def upload_files(files):
    """
    Streamlitでアップロードされたファイルまたはファイルのリストを一時ファイルに保存する
    
    Args:
        files: 単一のUploadedFileオブジェクト、またはUploadedFileオブジェクトのリスト
    
    Returns:
        list: [(一時パス, オリジナルファイル名), ...] のリスト
    
    Examples:
        # 単一ファイル
        pdf = st.file_uploader('PDF', type=['pdf'])
        file_info = upload_files(pdf)
        
        # 複数ファイル
        pdfs = st.file_uploader('PDFs', type=['pdf'], accept_multiple_files=True)
        files_info = upload_files(pdfs)
    """
    file_info = []
    
    # 単一ファイルの場合はリストに変換
    if not isinstance(files, list):
        files = [files]
    
    for uploaded_file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_info.append((tmp_file.name, uploaded_file.name))
            print(f"ファイル書き込み完了 ファイルパス: {tmp_file.name}")
    
    return file_info
