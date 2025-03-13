#!/bin/bash

# ESG・金融特化型AIリサーチアシスタント - 起動スクリプト

echo "ESG・金融特化型AIリサーチアシスタントを起動しています..."

# 仮想環境を有効化
source env/bin/activate

# .envファイルから環境変数を読み込む
if [ -f .env ]; then
  export $(cat .env | xargs)
fi

# OpenAI APIキーが設定されているか確認
if [ -z "$OPENAI_API_KEY" ]; then
  echo "警告: OpenAI APIキーが設定されていません。./setup.sh を実行してセットアップしてください。"
  exit 1
fi

# バックエンドAPIサーバーを起動（バックグラウンドで）
echo "1. バックエンドAPIサーバーを起動しています..."
python src/backend/api.py &
BACKEND_PID=$!
echo "APIサーバーが起動しました (PID: $BACKEND_PID)"

# スケジューラを起動
echo "2. スケジューラを起動しています..."
python src/main.py start

# フロントエンドの開発サーバーを起動
echo "3. フロントエンド開発サーバーを起動しています..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..
echo "フロントエンド開発サーバーが起動しました (PID: $FRONTEND_PID)"

echo "すべてのサービスが起動しました！"
echo "フロントエンドUI: http://localhost:3000"
echo "バックエンドAPI: http://localhost:5000"
echo ""
echo "終了するにはCtrl+Cを押してください。"

# 終了時にすべてのプロセスをクリーンアップ
cleanup() {
  echo "アプリケーションをシャットダウンしています..."
  kill $BACKEND_PID 2>/dev/null
  kill $FRONTEND_PID 2>/dev/null
  python src/main.py stop 2>/dev/null
  echo "シャットダウンが完了しました。"
  exit 0
}

# SIGINTシグナルをトラップ（Ctrl+C）
trap cleanup SIGINT

# スクリプトが終了されるまで待機
wait