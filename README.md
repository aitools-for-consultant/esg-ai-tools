# ESG・金融特化型AIリサーチアシスタント

AIを活用してESG（環境・社会・ガバナンス）と金融分野の研究論文を収集、分析し、インサイトを提供する自動化された研究アシスタントです。

## 機能

- **自動データ収集**: arXivなどのソースから定期的に最新の研究論文を取得
- **AI分析**: 論文の要約、重要な洞察の抽出、研究ブリーフの生成
- **セマンティック検索**: キーワードだけでなく意味に基づいて論文を検索
- **研究ブリーフ生成**: ESG/金融の特定トピックに関するAI生成ブリーフ
- **スケジューリング**: データ収集と処理タスクの設定可能なスケジューリング

## アーキテクチャ

- **バックエンド**: AI処理のためのOpenAIエージェントを使用したPython
- **フロントエンド**: ユーザーインターフェース用のTypeScript/React
- **データベース**: データストレージ用のSQLite
- **API**: Flaskを使用したRESTful API

## 要件

- Python 3.8以上
- Node.js 14以上
- OpenAI APIキー

## インストール

### バックエンドのセットアップ

1. リポジトリをクローン:
```bash
git clone https://github.com/yourusername/esg-ai-tools.git
cd esg-ai-tools
```

2. 仮想環境を作成して有効化:
```bash
python -m venv env
source env/bin/activate  # Windowsの場合: env\Scripts\activate
```

3. Pythonの依存関係をインストール:
```bash
pip install -r requirements.txt
```

4. OpenAI APIキーを設定:
```bash
export OPENAI_API_KEY=your_openai_api_key
# Windowsの場合: set OPENAI_API_KEY=your_openai_api_key
```

### フロントエンドのセットアップ

1. frontendディレクトリに新しいReact TypeScriptプロジェクトを作成:
```bash
npx create-react-app frontend --template typescript
cd frontend
```

2. 必要なnpmパッケージをインストール:
```bash
npm install axios react-router-dom
```

3. `src/frontend`からReactプロジェクトの適切なディレクトリにフロントエンドコードファイルをコピー。

## 使用方法

### バックエンド

1. データベースを初期化:
```bash
python src/backend/database.py
```

2. APIサーバーを起動:
```bash
python src/backend/api.py
```

3. 別のターミナルで、CLIを使用してアプリを管理:
```bash
# スケジューラを開始
python src/main.py start

# スケジューラのステータスを確認
python src/main.py status

# すぐに論文を収集
python src/main.py collect

# すぐに論文を処理
python src/main.py process

# 論文をリスト表示
python src/main.py list

# 研究ブリーフを生成
python src/main.py brief "気候金融が企業ガバナンスに与える影響"
```

### フロントエンド

1. frontendディレクトリでReact開発サーバーを起動:
```bash
npm start
```

2. ブラウザで http://localhost:3000 にアクセスしてUIを使用。

## 設定

設定オプションは`config/config.py`に保存されており、以下を含みます:

- APIキー
- データソースとカテゴリ
- スケジュール間隔
- AIモデルパラメータ

## データソース

現在、システムは以下をサポートしています:

- **arXiv**: 金融、経済学、統計学の論文
- **SSRN**: ESGと金融関連のトピック（注：SSRNのAPIアクセスは制限されています）

## 主要コンポーネント

### バックエンド

- `src/main.py`: メインCLIエントリポイント
- `src/backend/api.py`: RESTful API
- `src/backend/database.py`: データベースモデルと操作
- `src/backend/data_collectors.py`: ソースからの論文収集
- `src/backend/ai_processing.py`: OpenAIエージェントを使用したAI分析
- `src/backend/scheduler.py`: 自動化のためのスケジューリング

### フロントエンド

- `src/frontend/App.tsx`: メインReactアプリケーション
- `src/frontend/pages/HomePage.tsx`: メインページコンポーネント
- `src/frontend/components/`: UIコンポーネント
- `src/frontend/services/api.ts`: APIクライアント
- `src/frontend/hooks/useApi.ts`: カスタムReactフック
- `src/frontend/types/types.ts`: TypeScriptインターフェース

## ライセンス

MIT

## 謝辞

このプロジェクトは以下のオープンソースパッケージを使用しています:

- [OpenAI Agents Python](https://github.com/openai/openai-agents-python)
- [React](https://reactjs.org/)
- [Flask](https://flask.palletsprojects.com/)