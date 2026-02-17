# プロジェクト構造

## ディレクトリ構成

```
scout_automation/
│
├── models/                      # データモデル層
│   ├── __init__.py             # 共通エクスポート
│   ├── scout_models.py         # Scout関連モデル
│   └── jd_models.py            # JD関連モデル
│
├── clients/                     # 外部サービスクライアント層
│   ├── gemini_client.py        # Gemini API クライアント
│   ├── openai_client.py        # OpenAI API クライアント
│   └── google_client.py        # Google API クライアント
│
├── services/                    # ビジネスロジック層
│   ├── scout/                  # スカウト機能
│   │   ├── main.py
│   │   ├── logic.py
│   │   ├── ai_matching.py
│   │   └── create_prompt_logic.py
│   │
│   ├── jd/                     # 求人票作成機能
│   │   ├── main.py
│   │   ├── logic.py
│   │   └── preparation_ai.py
│   │
│   └── screening/              # スクリーニング機能
│       ├── main.py
│       ├── logic.py
│       └── preparation_ai.py
│
├── app.py                      # アプリケーションエントリーポイント
└── .streamlit/
    └── secrets.toml            # 環境変数・機密情報
```

## 各層の責任

### Models層
**責任**: データ構造の定義
- Pydanticモデルの定義
- バリデーションルール
- データの型定義

**依存**: なし（純粋なデータモデル）

### Clients層
**責任**: 外部APIとの通信
- API呼び出しの実装
- エラーハンドリング
- リトライロジック
- ファイルアップロード/ダウンロード

**依存**: `models` (レスポンスのパース用)

### Services層
**責任**: ビジネスロジック
- ユースケースの実装
- データの加工・変換
- 複数のクライアントの組み合わせ
- ドメイン固有のロジック

**依存**: `clients`, `models`

## モデル一覧

### Scout Models (`models/scout_models.py`)
| モデル名 | 用途 | 主な使用箇所 |
|---------|------|------------|
| `AiResult` | AI評価結果の個別レコード | `ai_matching.py` |
| `ResultsContainer` | AI評価結果の複数レコードのコンテナ | `ai_matching.py` |
| `CreatePromptModel` | プロンプト作成結果 | `create_prompt_logic.py` |
| `ScoutMaterialModel` | スカウト素材（検索条件、文面） | `logic.py` |

### JD Models (`models/jd_models.py`)
| モデル名 | 用途 | 主な使用箇所 |
|---------|------|------------|
| `OfferingContentModel` | 募集要項の構造化データ | `jd/logic.py` |
| `BussinessDescriptionModel` | 事業概要の構造化データ | `jd/logic.py` |

## インポートパターン

### 推奨パターン（新しいコード）
```python
# モデルを直接インポート
from models.scout_models import ResultsContainer, AiResult
from models.jd_models import OfferingContentModel

# クライアントをインポート
from clients import gemini_client

# 使用
result = gemini_client.request_with_files_by_parallel(
    prompt, files, job_file, ResultsContainer
)
```

### 後方互換パターン（既存コード）
```python
# クライアント経由でモデルにアクセス（非推奨だが動作する）
from clients import gemini_client

# 使用
result = gemini_client.request_with_files_by_parallel(
    prompt, files, job_file, gemini_client.ResultsContainer
)
```

## アーキテクチャの利点

### 1. 疎結合
各層が独立しており、変更の影響範囲が限定的

### 2. テスト容易性
- Models: 単体でバリデーションテスト可能
- Clients: モックサーバーでテスト可能
- Services: モッククライアントでテスト可能

### 3. 再利用性
モデルやクライアントを複数のサービスで共有可能

### 4. 保守性
責任が明確で、コードの位置が予測しやすい

## 今後の拡張

### 新しいサービスを追加する場合
1. `models/`に新しいモデルファイルを作成
2. `models/__init__.py`に追加
3. `services/`に新しいサービスディレクトリを作成
4. 既存のクライアントを再利用、または新しいクライアントを追加

### 新しいモデルを追加する場合
1. 適切なモデルファイル（`scout_models.py`など）に追加
2. `models/__init__.py`の`__all__`に追加
3. 必要に応じてクライアント関数のシグネチャを更新
