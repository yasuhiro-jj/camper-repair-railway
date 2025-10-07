# Anacondaプロンプトでの実行手順

## 🐍 Anaconda環境でのセットアップ

### 1. Anacondaプロンプトを開く
- Windowsキー + R を押して「cmd」と入力
- または、スタートメニューから「Anaconda Prompt」を検索して起動

### 2. プロジェクトディレクトリに移動
```bash
cd C:\Users\user\Desktop\udemy-langchain\camper-repair-clean
```

### 3. 新しいconda環境を作成（推奨）
```bash
# 新しい環境を作成
conda create -n camper-repair python=3.9

# 環境をアクティベート
conda activate camper-repair
```

### 4. 依存関係をインストール
```bash
# pipでインストール
pip install -r requirements.txt

# または、condaでインストール（可能な場合）
conda install -c conda-forge streamlit pandas
pip install langchain langchain-openai openai pypdf google-search-results python-dotenv flask langchain-chroma chromadb requests langgraph typing-extensions notion-client
```

### 5. 環境変数の設定
```bash
# .envファイルを作成
echo OPENAI_API_KEY=your_openai_api_key_here > .env
echo NOTION_API_KEY=your_notion_api_key_here >> .env
echo NODE_DB_ID=your_notion_node_db_id >> .env
echo CASE_DB_ID=your_notion_case_db_id >> .env
echo ITEM_DB_ID=your_notion_item_db_id >> .env
```

### 6. アプリケーションの起動

#### 方法1: Flaskアプリ（推奨）
```bash
python app.py
```
- ブラウザで http://localhost:5000 にアクセス

#### 方法2: Streamlitアプリ
```bash
streamlit run streamlit_app.py
```
- ブラウザで http://localhost:8501 にアクセス

#### 方法3: 起動スクリプトを使用
```bash
python run_app.py
```

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. パッケージのインストールエラー
```bash
# conda-forgeチャンネルを追加
conda config --add channels conda-forge

# 個別にインストール
conda install streamlit pandas numpy
pip install langchain langchain-openai
```

#### 2. 環境変数の問題
```bash
# 環境変数を確認
echo %OPENAI_API_KEY%

# 手動で設定
set OPENAI_API_KEY=your_api_key_here
```

#### 3. ポートが使用中
```bash
# 別のポートで起動
streamlit run streamlit_app.py --server.port 8502
# または
python app.py --port 5001
```

#### 4. 権限エラー
```bash
# 管理者権限でAnacondaプロンプトを実行
# または、ユーザーディレクトリに移動
cd %USERPROFILE%\Desktop\udemy-langchain\camper-repair-clean
```

## 📋 実行前チェックリスト

- [ ] Anacondaプロンプトが起動している
- [ ] 正しいディレクトリに移動済み
- [ ] conda環境がアクティベート済み
- [ ] 依存関係がインストール済み
- [ ] .envファイルが作成済み
- [ ] APIキーが正しく設定済み

## 🚀 クイックスタート（一括実行）

```bash
# 1. ディレクトリ移動
cd C:\Users\user\Desktop\udemy-langchain\camper-repair-clean

# 2. 環境作成とアクティベート
conda create -n camper-repair python=3.9 -y
conda activate camper-repair

# 3. 依存関係インストール
pip install -r requirements.txt

# 4. 環境変数設定（.envファイルを手動で作成）
# 5. アプリ起動
python app.py
```

## 📝 注意事項

1. **Pythonバージョン**: Python 3.8以上を推奨
2. **メモリ使用量**: アプリケーションは約500MB-1GBのメモリを使用
3. **ネットワーク**: OpenAI APIへの接続が必要
4. **ブラウザ**: モダンブラウザ（Chrome、Firefox、Edge）を推奨

## 🔄 環境の管理

### 環境の削除
```bash
conda deactivate
conda env remove -n camper-repair
```

### 環境の一覧表示
```bash
conda env list
```

### パッケージの更新
```bash
pip install --upgrade -r requirements.txt
```
