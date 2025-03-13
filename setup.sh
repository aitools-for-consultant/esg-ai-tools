#!/bin/bash

# ESG・金融特化型AIリサーチアシスタント - セットアップスクリプト

echo "ESG・金融特化型AIリサーチアシスタントのセットアップを開始します..."

# Python環境のセットアップ
echo "1. Python仮想環境をセットアップしています..."
python -m venv env

# 仮想環境を有効化
source env/bin/activate

# Pythonの依存関係をインストール
echo "2. Pythonの依存関係をインストールしています..."
pip install -r requirements.txt

# フロントエンドのセットアップ確認
echo "3. フロントエンドのセットアップを確認しています..."
if [ ! -d "frontend/node_modules" ]; then
  echo "フロントエンドの依存関係をインストールします..."
  cd frontend
  npm install
  cd ..
fi

# データベースの初期化
echo "4. データベースを初期化しています..."
python src/backend/database.py

# OpenAI APIキーの設定
echo "5. OpenAI APIキーの設定"
read -p "OpenAI APIキーを入力してください: " api_key
export OPENAI_API_KEY=$api_key
echo "OPENAI_API_KEY=$api_key" > .env

echo "セットアップが完了しました！"
echo "アプリケーションを起動するには ./start.sh を実行してください。"