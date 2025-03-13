#!/bin/bash
# ESG・金融特化型AIリサーチアシスタント - 停止スクリプト
echo "ESG・金融特化型AIリサーチアシスタントを停止しています..."

# 仮想環境を有効化
source env/bin/activate

# バックエンドAPIサーバーのプロセスを検索して停止
echo "1. バックエンドAPIサーバーを停止しています..."
pkill -f "python src/backend/api.py" || echo "バックエンドAPIサーバーは実行されていないようです。"

# スケジューラを停止
echo "2. スケジューラを停止しています..."
python src/main.py stop || echo "スケジューラは実行されていないようです。"

# フロントエンドの開発サーバーを停止
echo "3. フロントエンド開発サーバーを停止しています..."
npx kill-port 3000 || pkill -f "node.*react-scripts start" || echo "フロントエンド開発サーバーは実行されていないようです。"

echo "すべてのサービスを停止しました！"