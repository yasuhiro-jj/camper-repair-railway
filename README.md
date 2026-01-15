# 🚐 キャンピングカー修理チャットボット

Notion統合型の最強キャンピングカー修理サポートシステム

## 🌟 主な機能

### 1. 💬 AI チャットボット
- OpenAI GPT-4搭載
- 自然な会話で修理相談
- 過去の会話履歴を記憶

### 2. 🔍 修理アドバイスセンター
- **Notion統合検索**
- 費用目安の自動表示
- 難易度・推定時間の表示
- 柔軟なキーワード検索

### 3. 🩺 診断フロー
- Notionベースの診断システム
- インタラクティブな質問フロー
- 症状に基づいた原因特定

### 4. 📚 ナレッジベース (RAG)
- ChromaDBによるベクトル検索
- 24カテゴリの修理情報
- リアルタイム検索

### 5. 📱 LINE通知機能
- **ブラウザ版チャットボット**でやり取り
- **LINE Login**でユーザー認証・ユーザーID取得
- **LINE Messaging API**でプッシュ通知送信
- Notionデータベースから自動通知（修理完了、ステータス更新など）
- リッチなFlexメッセージ対応

### 6. 🎯 修理工場マッチングLP（お客様用）
- **キャンピングカー修理工場マッチングLP（お客様用）** (`/lp-camper-repair`)
- キャンピングカー所有者（お客様）向けの修理工場マッチングLP
- 修理工場・大工・公務店・自動車整備工場を探せるサービス
- AI診断と自動マッチング機能の紹介
- キャンピングカー修理の現状と課題の説明
- 利用の流れの説明
- 問い合わせフォーム（ユーザー向け）
- SEO最適化済み（メタタグ、構造化データ）

### 7. 🏭 パートナー募集LP（修理工場向け）
- **キャンピングカー修理パートナー募集LP** (`/lp-partner-recruit`)
- 修理工場・大工・公務店・自動車整備工場・個人職人向けの募集LP
- 専門業者でなくても参画できることを強調
- パートナーになるメリットの説明
- 修理依頼の流れの説明
- 料金モデル（登録無料、手数料10〜20%）の説明
- 事例紹介とFAQ
- パートナー登録フォーム
- SEO最適化済み（メタタグ、構造化データ）



【リポジトリ】
C:\Users\PC user\OneDrive\Desktop\移行用まとめフォルダー\udemy-langchain\camper-repair-clean

## 📊 システム全体の流れ（ビジネスフロー）

このシステムは、**キャンピングカー修理の集客から入金まで**を自動化する仕組みです。修理工場の社長様は、スマホひとつで「確認」「連絡&修理」「報告」の3つだけをやればOK。あとはシステムが自動で動きます。

### 🎯 全体像：3つのステップ

```
STEP1: 集客（お客様が工場を見つける）
    ↓
STEP2: 対応（修理受付から完了まで）
    ↓
STEP3: 決済・評価（お金の流れと次の集客へ）
```

---

### STEP1: お客様が工場を見つけるまで（集客）

**お客様の行動：**
1. キャンピングカーで困ったことが発生（例：「エアコンが効かない...困った」）
2. スマホでAIチャットボットに相談
3. AIが24時間対応で症状を診断し、最適な修理工場を提案
4. お客様が「この工場に決定！」→問い合わせを送信

**システムの動き：**
- AIチャットボットが症状を分析
- 地域や修理内容に合わせて最適な工場を自動マッチング
- 問い合わせが工場に届く
- 検索順位が自動的に上がる（良い評価が集まるほど）

**社長様のやること：**
- ✅ 届いた案件を確認（スマホで通知が来る）

---

### STEP2: 修理受付から完了まで（対応）

**社長様の行動：**
1. **通知を受け取る**
   - LINEまたはメールで「新規案件が届きました！」と通知
   - スマホで確認

2. **ダッシュボードで確認**
   - 工場専用ダッシュボードを開く
   - 症状（例：エアコン故障）を確認
   - 必要なら作業マニュアルも確認OK

3. **お客様と直接連絡**
   - 電話またはLINEで連絡
   - 「お電話ありがとうございます！日程調整しましょう！」
   - 修理日時を決める

4. **修理を実施**
   - 現場で修理作業
   - 必要に応じて作業マニュアルを参照

5. **完了報告**
   - ダッシュボードで「完了」ボタンを押すだけ

**システムの動き：**
- 問い合わせを自動で案件化
- 作業マニュアルを自動提供
- ステータスを自動管理
- 完了時に自動でお客様に通知

**社長様のやること：**
- ✅ 確認（ダッシュボードで案件を見る）
- ✅ 連絡&修理（お客様と連絡して修理する）
- ✅ 報告（完了ボタンを押す）

---

### STEP3: お金の流れと次の集客へ（決済・評価）

**お客様の行動：**
1. 修理完了&支払い案内のメール/LINE通知を受け取る
2. 指定口座に振り込む

**お金の流れ（重要）：**
1. **お客様が支払う**
   - お客様は「工場に支払う」と思っている（建前）
   - 実際は「サポートセンター専用口座」に振り込まれる

2. **システムが一旦預かる**
   - サポートセンター専用口座に一旦入金
   - システムが自動で管理

3. **手数料を差し引く**
   - 手数料（30%）を自動計算して差し引き

4. **工場に自動入金**
   - 残額（70%）が自動的に工場口座に振り込まれる
   - 「売上ゲット！」の通知が来る

**評価と次の集客：**
1. お客様が評価を入力（5つ星評価など）
   - 「すごく助かりました！ありがとう！」
2. 良い評価が集まると検索順位がUP
3. 次のお客様が自然に見つけてくる
4. またSTEP1に戻る（好循環）

**社長様のやること：**
- ✅ 何もしなくてOK！自動で入金されます

---

### 💡 このシステムの3つのメリット

#### 1. **社長様の負担が最小限**
- やることは「確認」「連絡&修理」「報告」の3つだけ
- 面倒な事務作業（問い合わせ対応、請求書作成、入金管理など）は全て自動化

#### 2. **24時間自動集客**
- AIチャットボットが24時間対応
- お客様が困った時にすぐ相談できる
- 良い評価が集まると自動的に検索順位が上がる

#### 3. **お金の流れが透明**
- 手数料（30%）と工場への支払い（70%）が自動計算
- 入金も自動で行われるので、請求書作成や入金確認の手間がない

---

### 🎬 実際の流れの例

**例：エアコン故障の修理**

1. **お客様**：「エアコンが効かない...」→ AIチャットボットに相談
2. **AI**：「エアコン故障ですね。○○工場が最適です」→ 問い合わせ送信
3. **社長様**：スマホに通知「新規案件が届きました！」
4. **社長様**：ダッシュボードで確認 → お客様に電話「日程調整しましょう」
5. **社長様**：現場で修理 → ダッシュボードで「完了」ボタン
6. **システム**：お客様に「修理完了&支払い案内」を自動送信
7. **お客様**：振り込み → 評価入力「5つ星！」
8. **システム**：手数料30%を差し引き → 残り70%を工場に自動入金
9. **システム**：良い評価で検索順位UP → 次のお客様が来る

**社長様がやったこと：確認 → 連絡&修理 → 報告（完了ボタン）**

これだけです！

---

## 🏗️ システム構成

### バックエンド
- **Flask** - Webフレームワーク
- **Python 3.10+** - プログラミング言語
- **Gunicorn** - WSGIサーバー

### データソース
- **Notion Database** - メインデータストア
  - 修理ケースDB
  - 診断フローDB
  - 部品・工具DB
  - ナレッジベースDB
- **ChromaDB** - ベクトル検索
- **OpenAI Embeddings** - テキスト埋め込み

### AI・検索
- **OpenAI GPT-4** - AI応答生成
- **LangChain** - AI統合フレームワーク
- **SERP API** - リアルタイム価格検索（オプション）

## 🔭 将来拡張計画：マニュアル連携＋SerpAPI検索チャットボット

このプロジェクトでは将来、**「作業マニュアル × チャットボット × SerpAPI（Web検索）」** を組み合わせたサポート体制の実装を検討している。

### 1. 想定するユースケース

- 整備工場の担当者が、キャンピングカー修理に関する疑問をチャットボットに質問する  
- まずは社内マニュアル・自前ナレッジを優先して回答  
- それでも「もっと詳しく」「最新の情報」「他社事例」が必要な場合に、SerpAPIを用いてWeb検索し、情報を補完する  

### 2. チャットボットの基本フロー（構想レベル）

1. **ユーザー質問受付**  
   - 例：「このFFヒーターのエラーコードE-03は、どう診断すればいいですか？」

2. **質問の解析・分類**  
   - 車種・装備（FFヒーター／サブバッテリーなど）  
   - 症状（エラーコード・異音・動作不良など）を抽出

3. **社内マニュアル優先検索**  
   - 社内マニュアル・診断フロー・FAQをもとに回答を生成  
   - 「マニュアルだけで十分かどうか」を内部的に判定（信頼度スコア）

4. **マニュアルで足りる場合**  
   - マニュアルベースの回答を提示  
   - 必要に応じて関連手順・注意点もあわせて表示  
   - この段階ではSerpAPIは呼ばない

5. **「もっと詳しく」トリガー**  
   - ユーザーが「もっと詳しく」「他の事例」「最新情報」などを要求、  
     もしくはボットが「情報が薄い／古い可能性あり」と判断した場合、  
     「▶ さらに詳しい情報をインターネットから探してきましょうか？」と提案

6. **SerpAPI検索フェーズ**  
   - ユーザーが了承した場合のみSerpAPIを実行  
   - 質問内容から検索クエリを生成し、SerpAPIでWeb検索  
   - 関連性の高い結果を抽出し、要約

7. **マニュアル＋外部情報の統合回答**  
   - 社内マニュアルの内容と、SerpAPIから取得した情報を統合して提示  
   - 必要に応じて「社内情報由来」「Web情報由来」を区別して扱う

8. **安全チェック（キャンピングカー特有の注意）**  
   - ガス・燃焼系（FFヒーター内部改造など）  
   - 高電圧・大容量バッテリー  
   - 車体構造に関わる大きな加工  
   を含む場合は、必ず最後に安全上の注意を自動付与：  
   - 「安全上、ここから先は専門業者に相談してください」  
   - 「法令・保安基準に関わる可能があります」

9. **追加質問ループ**  
   - ユーザーの追い質問に対して、上記 3〜8 を繰り返す

### 3. マニュアル側に記載する想定文例（案）

> 本マニュアルでは、FFヒーター故障時の基本的な診断手順を説明しています。  
> 個別車種・年式ごとの事例や、より詳しい最新情報が必要な場合は、  
> **「キャンピングカー修理サポートチャットボット」にエラー内容と症状を入力してください。**  
> チャットボットは本マニュアルの内容に加え、必要に応じてインターネット検索（SerpAPI）も併用し、  
> より詳細な診断のヒントや注意点を提示します。

※本機能は現時点では「将来の拡張計画」であり、まだ実装されていません。今後、LLMプラットフォーム＋SerpAPI連携を用いて段階的に導入する予定です。

## 📦 主要な依存関係

```
Flask>=2.3.0
Flask-CORS>=4.0.0
langchain>=0.1.0
langchain-openai>=0.1.0
python-dotenv>=1.0.0
notion-client>=2.2.1
aiohttp>=3.8.0
chromadb>=0.4.0
sentence-transformers>=2.2.0
openai>=1.0.0
requests>=2.31.0
gunicorn>=21.2.0
```

## 🚀 ローカルセットアップ

### クイックスタート（概要）

1. **環境変数を設定**（`.env`ファイルを作成）
2. **依存関係をインストール**（バックエンド・フロントエンド）
3. **バックエンドを起動**（Anaconda Prompt）
4. **フロントエンドを起動**（別ターミナル）
5. **ブラウザでアクセス**（http://localhost:3000）

詳細な手順は以下を参照してください。

---

### 1. リポジトリをクローン

```bash
git clone [your-repo-url]
cd camper-repair-clean
```

### 2. 環境変数を設定

#### バックエンドの環境変数

プロジェクトルートに`.env`ファイルを作成（`env.example`を参考）：

```bash
# .envファイルを作成
OPENAI_API_KEY=your_openai_api_key
NOTION_API_KEY=your_notion_api_key
NODE_DB_ID=your_diagnostic_flow_db_id
CASE_DB_ID=your_repair_case_db_id
ITEM_DB_ID=your_parts_tools_db_id
KNOWLEDGE_BASE_DB_ID=2d099e34964341d4ba39b291f24d6b6b

# 工場DB（工場マッチング機能用）
NOTION_FACTORY_DB_ID=c0df759557bb4b088492760ae3c8bc4a

# メール通知機能（Resend推奨）
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Resend無料運用の例（独自ドメイン未設定の場合）
FROM_EMAIL=onboarding@resend.dev

# メール通知機能（SMTPフォールバック - オプション）
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# LINE通知機能（オプション）
LINE_CHANNEL_ID=your_line_channel_id
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_LOGIN_CALLBACK_URL=https://your-domain.com/api/line/login/callback

# 支払い案内用の口座情報（オプション）
PAYMENT_BANK_NAME=○○銀行
PAYMENT_BANK_BRANCH=○○支店
PAYMENT_ACCOUNT_NUMBER=1234567
PAYMENT_ACCOUNT_NAME=岡山キャンピングカー修理サポートセンター

# フロントエンドURL（本番環境用）
FRONTEND_URL=https://camper-repair-railway-upoj.vercel.app
```

**重要**: `.env`ファイルが存在しないとバックエンドが起動できません。

#### フロントエンドの環境変数

`frontend/.env.local`ファイルを作成（オプション、デフォルト値で動作します）：

```env

バックエンド

NEXT_PUBLIC_API_URL=https://web-development-8c2f.up.railway.app

フロントエンド
https://camper-repair-railway-upoj.vercel.app/
```

**注意**: `.env.local`ファイルが存在しない場合、フロントエンドはデフォルトで`http://localhost:5002`を使用します。

### 3. 依存関係をインストール

#### バックエンドの依存関係

Anaconda Promptで実行：

```bash
# conda環境をアクティベート（環境が存在する場合）
conda activate campingrepare

# 依存関係をインストール
python -m pip install -r requirements.txt
```

**注意**: 
- `pip install`がエラーになる場合は、`python -m pip install`を使用してください
- `campingrepare`環境が存在しない場合は、先に環境を作成してください：
```bash
conda create -n campingrepare python=3.9 -y
conda activate campingrepare
python -m pip install -r requirements.txt
```

**トラブルシューティング**:
- `pip install`でエラーが発生する場合：
  ```bash
  # Pythonを直接使ってpipを実行
  python -m pip install -r requirements.txt
  ```
- それでも解決しない場合：
  ```bash
  # condaで主要パッケージをインストール
  conda install flask flask-cors python-dotenv requests pyyaml -y
  # 残りをpipでインストール
  python -m pip install langchain langchain-openai langchain-community langchain-chroma notion-client aiohttp chromadb sentence-transformers openai gunicorn streamlit "numpy<2.0.0"
  ```


バックエンド起動（Anaconda Prompt）

   cd "C:\Users\PC user\OneDrive\Desktop\移行用まとめフォルダー\udemy-langchain\camper-repair-clean"
   conda activate campingrepare
   python unified_backend_api.py

   


フロントエンド起動（別ターミナル）

   cd "C:\Users\PC user\OneDrive\Desktop\移行用まとめフォルダー\udemy-langchain\camper-repair-clean\frontend"
   conda activate campingrepare   # 必要なら
   npm run dev








#### フロントエンドの依存関係

# 1. Conda環境をアクティベート
conda activate campingrepare

# 2. フロントエンドディレクトリに移動（このREADMEと同じ階層にあるfrontend）
# 例: cd "C:\path\to\camper-repair-clean\frontend"
cd frontend

# 3. 初回のみ：依存関係をインストール（まだの場合）
npm install

# 4. 開発サーバーを起動
npm run dev

**起動確認:**
- 以下のメッセージが表示されれば成功：
  ```
  ▲ Next.js 16.0.3
  - Local:        http://localhost:3000
  ✓ Ready in X.XXs
  ```

**動作確認:**
1. **ブラウザでアクセス**: http://localhost:3000 にアクセスできるか確認
2. **バックエンド接続確認**: チャットボットや修理店検索が動作するか確認
3. **エラー確認**: ブラウザのコンソール（F12）でエラーが出ていないか確認
4. **主要機能の確認**:
   - チャットボットが応答するか
   - 修理店検索が動作するか（「東京」で「東京都」の修理店が検索できるか）
   - ページ遷移が正常に動作するか

**エラーが発生した場合:**
- バックエンドが起動しているか確認（http://localhost:5002）
- `npm install`が完了しているか確認
- ポート3000が使用中でないか確認
- `.env.local`ファイルの設定を確認（必要に応じて）







## 🚀 クイックスタート

### 起動手順の概要

1. **バックエンドを起動**（Anaconda Prompt）
2. **フロントエンドを起動**（別ターミナル：コマンドプロンプトまたはPowerShell）
3. **ブラウザでアクセス**（http://localhost:3000）

**重要**: バックエンドとフロントエンドは**別々のターミナル**で起動してください。

---




### 4. バックエンドを起動

**Anaconda Promptで実行：**

```bash
# プロジェクトディレクトリに移動（このREADMEと同じフォルダ）
# 例: cd "C:\path\to\camper-repair-clean"
cd camper-repair-clean

# conda環境をアクティベート
conda activate campingrepare

# .envファイルの存在確認（重要）
# .envファイルが存在しない場合は、ステップ2に戻って作成してください

# バックエンドを起動
python unified_backend_api.py
```






**起動確認:**
- 以下のメッセージが表示されれば成功：
  ```
  ✅ 全サービスが正常に初期化されました
  🌐 アクセスURL: http://localhost:5002
  ```
- サーバーが起動すると、以下のようなメッセージが表示されます：
  ```
  * Running on http://127.0.0.1:5002
  * Running on http://192.168.150.69:5002
  ```

**バックエンドの役割:**
- APIサーバーとして動作（フロントエンドからのリクエストを処理）
- データベース（Notion、ChromaDB）との連携
- AI処理（GPT-4、RAG検索など）
- APIドキュメント（Swagger UI）の提供

**エラーが発生した場合:**
- `.env`ファイルが存在するか確認
- 必要な環境変数がすべて設定されているか確認
- ポート5002が使用中でないか確認
- 依存関係がインストールされているか確認（`python -m pip install -r requirements.txt`）

**注意**: バックエンドは起動したままにしてください。別のターミナルでフロントエンドを起動します。

---

### 5. フロントエンドを起動（別ターミナル）

**重要**: バックエンドを起動したターミナルとは**別のターミナル**を開いてください。

**⚠️ 日本語パスの問題について:**
- Next.js 16 の Turbopack は日本語を含むパスで動作しません
- **解決策**: プロジェクトを英数字のみのパスにコピーしてください
- 推奨パス: `C:\next-camper\camper-repair-clean`

**プロジェクトのコピー手順:**
1. `C:\next-camper` フォルダを作成
2. `camper-repair-clean` フォルダ全体をコピー
3. 以下のコマンドで新しい場所から起動

**Anaconda Promptで実行：**

```bash
# フロントエンドディレクトリに移動（日本語パスを避けた新しい場所）
cd /d C:\next-camper\camper-repair-clean\frontend

# 初回のみ：依存関係をインストール
npm install

# 開発サーバーを起動
npm run dev
```

**元の場所（日本語パス）でも動かしたい場合:**
```bash
# ※非推奨：Turbopackエラーが発生する可能性があります
cd "C:\Users\PC user\OneDrive\Desktop\移行用まとめフォルダー\udemy-langchain\camper-repair-clean\frontend"
npm run dev
```

**起動確認:**
- 以下のメッセージが表示されれば成功：
  ```
  ▲ Next.js 16.0.3
  - Local:        http://localhost:3000
  ✓ Ready in X.XXs
  ```

**フロントエンドの役割:**
- ユーザー向けのUIを提供（チャットボット、修理店検索など）
- バックエンドAPIと通信
- レスポンシブデザイン（PC・スマホ対応）

**環境変数（オプション）**: `frontend/.env.local`ファイルを作成すると、バックエンドAPIのURLをカスタマイズできます：
```env
NEXT_PUBLIC_API_URL=https://web-development-8c2f.up.railway.app
```

**注意**: `.env.local`ファイルが存在しない場合でも、フロントエンドはデフォルトで`http://localhost:5002`を使用するため、正常に動作します。

---

### 6. ブラウザでアクセス

両方が起動したら、ブラウザで以下にアクセス：

#### 通常の使用（推奨）

**フロントエンド（ユーザー向けUI）:**
```
http://localhost:3000
```
- チャットボット
- 修理店検索
- 問い合わせフォーム
- LPページ

**LPページ:**
- お客様向け: http://localhost:3000/lp-camper-repair
- 業者向け: http://localhost:3000/lp-partner-recruit

#### 開発・デバッグ用

**バックエンドAPI（直接アクセス）:**
```
http://localhost:5002
```

**APIドキュメント（Swagger UI）:**
```
http://localhost:5002/api/docs
```
- APIエンドポイントの一覧
- リクエスト/レスポンスの仕様確認
- APIのテスト実行

**テストエンドポイント:**
```
http://localhost:5002/api/test
```

---

### 7. 停止方法

**バックエンドを停止:**
- バックエンドが起動しているターミナルで `Ctrl + C` を押す

**フロントエンドを停止:**
- フロントエンドが起動しているターミナルで `Ctrl + C` を押す

**注意**: 両方を停止する場合は、それぞれのターミナルで `Ctrl + C` を実行してください。

---

## 💾 バックアップと復旧

### バックアップの実行

プロジェクト全体をバックアップするには、Anaconda Promptで以下を実行：

```bash
# プロジェクトディレクトリに移動
cd "C:\Users\PC user\OneDrive\Desktop\移行用まとめフォルダー\udemy-langchain\camper-repair-clean"

# バックアップスクリプトを実行
python create_backup.py
```

または、バッチファイルを実行：

```bash
create_backup.bat
```

**バックアップ先:**
```
C:\Users\PC user\Desktop\camper-repair-backups\backup_YYYYMMDD_HHMMSS\
```

**バックアップされる内容:**
- ✅ バックエンドのPythonファイル
- ✅ `data_access/`フォルダ
- ✅ `frontend/`フォルダ（Next.jsアプリ）
- ✅ `templates/`フォルダ
- ✅ `static/`フォルダ
- ✅ 設定ファイル（`requirements.txt`など）
- ✅ ドキュメント（`README.md`など）

**除外される内容:**
- ❌ `.env`ファイル（セキュリティ上の理由）
- ❌ `node_modules/`（再インストール可能）
- ❌ `chroma_db/`（再生成可能）
- ❌ `__pycache__/`（自動生成）

**重要**: `.env`ファイルは別途安全な場所に手動でバックアップしてください。

---

### バックアップからの復旧

プロジェクトが消失したり、ファイルが破損した場合の復旧手順：

#### ステップ1: バックアップフォルダを確認

```bash
# バックアップフォルダを確認
dir "C:\Users\PC user\Desktop\camper-repair-backups"
```

利用可能なバックアップフォルダが表示されます（例: `backup_20251205_163817`）。

#### ステップ2: 新しいプロジェクトディレクトリを作成（必要に応じて）

プロジェクトが完全に消失している場合：

```bash
# 新しいプロジェクトディレクトリを作成（OneDrive外を推奨）
mkdir "C:\Projects\camper-repair-clean"
cd "C:\Projects\camper-repair-clean"
```

#### ステップ3: バックアップからファイルをコピー

**方法1: 手動でコピー（推奨）**

1. バックアップフォルダを開く：
   ```
   C:\Users\PC user\Desktop\camper-repair-backups\backup_YYYYMMDD_HHMMSS\
   ```

2. バックアップフォルダ内のすべてのファイルとフォルダを、プロジェクトディレクトリにコピー

3. 以下のフォルダが含まれているか確認：
   - `frontend/`
   - `data_access/`
   - `templates/`
   - `static/`
   - `unified_backend_api.py`
   - `requirements.txt`
   - その他のPythonファイル

**方法2: コマンドでコピー**

```bash
# バックアップフォルダを指定（実際のフォルダ名に置き換えてください）
set BACKUP_DIR=C:\Users\PC user\Desktop\camper-repair-backups\backup_20251205_163817

# プロジェクトディレクトリに移動
cd "C:\Users\PC user\OneDrive\Desktop\移行用まとめフォルダー\udemy-langchain\camper-repair-clean"

# バックアップからすべてのファイルをコピー
xcopy /E /I /H /Y "%BACKUP_DIR%\*" .
```

#### ステップ4: 環境変数ファイルを復元

`.env`ファイルを安全な場所から復元：

```bash
# .envファイルをコピー（安全な場所から）
copy "C:\Backups\camper-repair-env-backup.txt" .env
```

または、`env.example`をコピーして手動で設定：

```bash
copy env.example .env
# .envファイルを編集してAPIキーなどを設定
```

#### ステップ5: 依存関係をインストール

**バックエンドの依存関係:**

```bash
# Anaconda Promptで実行
conda activate campingrepare
python -m pip install -r requirements.txt
```

**フロントエンドの依存関係:**

```bash
# コマンドプロンプトまたはPowerShellで実行
cd frontend
npm install
```

#### ステップ6: システムの起動確認

**バックエンドを起動:**

```bash
# Anaconda Promptで実行
conda activate campingrepare
python unified_backend_api.py
```

**フロントエンドを起動（別ターミナル）:**

```bash
cd frontend
npm run dev
```

#### ステップ7: 動作確認

ブラウザで以下にアクセスして動作確認：

- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:5002
- APIドキュメント: http://localhost:5002/api/docs

---

### 復旧時の注意点

1. **`.env`ファイルの復元**
   - `.env`ファイルはバックアップに含まれていません
   - 別途安全な場所にバックアップした`.env`ファイルを復元してください
   - または、`env.example`をコピーして手動で設定してください

2. **`node_modules`の再インストール**
   - フロントエンドの`node_modules`はバックアップに含まれていません
   - `npm install`で再インストールしてください

3. **`chroma_db`の再生成**
   - ChromaDBはバックアップに含まれていません
   - バックエンド起動時に自動的に再生成されます

4. **conda環境の再作成**
   - conda環境が消失している場合は、再作成してください：
   ```bash
   conda create -n campingrepare python=3.9 -y
   conda activate campingrepare
   python -m pip install -r requirements.txt
   ```

5. **OneDriveの問題を避ける**
   - 復旧後は、プロジェクトをOneDrive外の場所に移動することを推奨します
   - 例: `C:\Projects\camper-repair-clean`

---

### 定期的なバックアップの推奨

- **週1回以上**のバックアップを推奨
- **重要な変更前後**にバックアップを実行
- **`.env`ファイル**は別途安全な場所にバックアップ
- **複数のバックアップ**を保持（最新の3〜5個）

---

## 📚 ドキュメント

### 技術ドキュメント
- [APIドキュメント](API_DOCUMENTATION.md) - APIの使用方法とクイックスタート
- [システムアーキテクチャ](ARCHITECTURE.md) - システム構成図とデータフロー図
- [コード整備ガイド](CODE_DOCUMENTATION.md) - コーディング規約と整備方針
- [OpenAPI仕様書](openapi.yaml) - OpenAPI 3.0形式のAPI仕様書

### 売却準備資料
- [Pitch Deck](PITCH_DECK.md) - プロジェクトの価値提案と機能紹介
- [デモ動画スクリプト](DEMO_VIDEO_SCRIPT.md) - デモ動画の撮影スクリプト
- [価値算定資料](VALUATION_REPORT.md) - 技術的価値とビジネス価値の算定
- [売却ロードマップ](売却_ROADMAP.md) - プロジェクトの全体ロードマップ

### テストガイド
- [チャットボット全体フローテスト](TEST_CHATBOT_FLOW.md) - チャットボットの主要機能をテスト
- [工賃推定機能テスト](TEST_COST_ESTIMATION.md) - AI工賃推定機能をテスト

### その他
- [CHANGELOG](CHANGELOG.md) - 変更履歴
- [SUMMARY](SUMMARY.md) - 売却準備完了サマリー

## 🌐 Railwayデプロイ

詳細は `RAILWAY_DEPLOY_GUIDE.md` を参照してください。

### クイックデプロイ

1. GitHubにプッシュ
2. [Railway](https://railway.app)でプロジェクト作成
3. 環境変数を設定
4. デプロイ完了！

## 📁 プロジェクト構造

```
camper-repair-clean/
├── unified_backend_api.py      # メインFlaskアプリ
├── enhanced_rag_system.py      # RAGシステム
├── data_access/
│   ├── notion_client.py        # Notion統合
│   ├── cost_estimation.py       # AI工賃推定エンジン
│   ├── factory_matching.py      # 工場マッチングエンジン
│   └── ...                      # その他のデータアクセス層
├── frontend/                    # Next.jsフロントエンド
│   ├── app/                     # Next.js App Router
│   │   ├── lp-camper-repair/   # キャンピングカー修理工場マッチングLP（お客様用）
│   │   ├── lp-partner-recruit/ # キャンピングカー修理パートナー募集LP（修理工場向け）
│   │   ├── chat/               # チャットボットページ
│   │   ├── partner/            # パートナー修理店紹介ページ
│   │   └── ...                 # その他のページ
│   ├── components/              # Reactコンポーネント
│   └── lib/                     # ユーティリティ関数
├── templates/
│   ├── unified_chatbot.html     # メインUI
│   └── repair_advice_center.html # 検索UI
├── openapi.yaml                 # OpenAPI仕様書
├── ARCHITECTURE.md              # システムアーキテクチャ図
├── API_DOCUMENTATION.md         # APIドキュメント
├── CODE_DOCUMENTATION.md        # コード整備ガイド
├── category_definitions.json    # カテゴリ定義
├── requirements.txt             # 依存関係
├── requirements_railway.txt     # 本番依存関係
├── Procfile                     # Railway設定
├── railway.json                 # Railway設定
└── RAILWAY_DEPLOY_GUIDE.md     # デプロイガイド
```

## 🔧 主要機能の実装

### 1. 柔軟な検索機能

キーワード抽出により自然な文章での検索が可能：

```python
# 「雨漏りがする」→ 「雨漏り」を抽出
# 助詞・動詞を自動除去
# 複数キーワードでOR検索
```

### 2. Notion統合

修理ケースDB優先の検索ロジック：

```python
1. 修理ケースDBを検索（費用情報あり）
2. 結果がなければ診断フローDBを検索
3. それでもなければ一般アドバイスを提供
```

### 3. 費用情報の表示

Notionから以下を自動取得：

- 💰 費用目安（詳細な内訳）
- ⚙️ 難易度（初級/中級/上級）
- ⏱️ 推定時間

## 🎯 使用例

### 修理検索

```
ユーザー: 「雨漏りがする」

システム: 
🔧 CASE-009
💰 費用目安:
  • 診断料：3,000〜5,000円
  • シーリング材交換：5,000〜15,000円
  • 窓枠修理：10,000〜30,000円
⚙️ 難易度: 中級
⏱️ 推定時間: 1時間〜4時間
```

### AI チャット

```
ユーザー: 「バッテリーが上がりやすいのですが、原因は何でしょうか？」

AI: 「バッテリーが上がりやすい場合、以下の原因が考えられます：
1. バッテリーの劣化（寿命3-5年）
2. オルタネーターの故障
3. 電装品の電力消費
...」
```

## 🔒 セキュリティ

- 環境変数に機密情報を保存
- `.gitignore`でAPIキーを除外
- Notion APIキーの権限を最小限に設定
- CORS設定を適切に管理

## 📊 カテゴリ一覧

24カテゴリの修理情報を網羅：

- 🔋 バッテリー
- ❄️ エアコン
- 🚽 トイレ
- 💧 水道ポンプ
- 🌧️ 雨漏り
- 🔌 インバーター
- ☀️ ソーラーパネル
- 🚪 ドア・窓
- 🔥 FFヒーター
- その他15カテゴリ

## 🛠️ 開発

### テストの実行

```bash
# 検索システムのテスト
python test_fixed_search.py

# 柔軟な検索のテスト
python test_flexible_search.py

# Notion接続のテスト
python debug_knowledge_base.py
```

### デバッグモード

```bash
# Flask開発サーバー
export FLASK_DEBUG=True
python unified_backend_api.py
```

## 📝 ライセンス

このプロジェクトは私的使用を目的としています。

## 🤝 貢献

プルリクエストを歓迎します！

## 📞 サポート

問題が発生した場合は、Issueを作成してください。

## 🎉 最新の改善（フェーズ2-3）

### ✅ 診断フロー改善機能（2025-11-17実装）

1. **質問文の自然化** (`improve_question_text.py`)
   - AIで質問を親しみやすい表現に変換
   - 専門用語を平易な言葉に置き換え
   
2. **フィードバックメッセージ生成** (`generate_feedback_messages.py`)
   - ユーザーの回答に共感的なフィードバック
   - 緊急度に応じた適切な応答
   
3. **AI症状分類** (`ai_symptom_classifier.py`)
   - 自由記述から症状カテゴリを自動判定
   - 確信度スコアと複数候補の提示
   
4. **診断フロー分析** (`analyze_diagnostic_flow.py`)
   - ボトルネック特定と改善提案
   - 統計情報の可視化

詳細は [フェーズ2-3_実装完了レポート.md](./フェーズ2-3_実装完了レポート.md) を参照

## 📄 LPページ詳細

### キャンピングカー修理工場マッチングLP（お客様用） (`/lp-camper-repair`)

キャンピングカー所有者（お客様）向けの修理工場マッチングランディングページです。修理工場・大工・公務店・自動車整備工場を簡単に探せるサービスを提供します。

#### 構成セクション（お客様用）

1. **ヒーローセクション**
   - キャッチコピー：「全国どこでも修理可能。キャンピングカーの "困った" を最短で解決。」
   - CTAボタン：無料診断

2. **課題セクション**
   - キャンピングカー修理の現状と課題を提示
   - 修理工場不足、ビルダー間の関係、西日本の工場不足など

3. **特徴セクション**
   - AI一次診断による故障内容の可視化
   - 全国の修理工場・大工・公務店との連携
   - AIによる自動マッチング

4. **利用の流れ**
   - 5ステップのフローチャート
   - チャットボット診断から修理完了まで

5. **問い合わせフォーム**
   - ユーザー（修理依頼）向けのフォーム
   - APIエンドポイント：`/api/inquiry`

6. **フッター**
   - 会社情報、リンク、連絡先

#### 技術仕様

- **フレームワーク**: Next.js 16 (App Router)
- **スタイリング**: TailwindCSS v4
- **デザイン**: 白 + ネイビー（slate-900）+ 黄色（yellow-400）
- **レスポンシブ**: スマホファースト
- **SEO**: メタタグ、Open Graph、構造化データ（LocalBusiness）

#### ファイル構成

```
frontend/app/lp-camper-repair/
├── layout.tsx              # SEOメタタグ設定
├── page.tsx                # メインページ
└── components/
    ├── Hero.tsx            # ヒーローセクション
    ├── Problem.tsx          # 課題セクション
    ├── Features.tsx        # 特徴セクション
    ├── ForPartners.tsx     # 修理工場向けメリット
    ├── Flow.tsx            # 利用の流れ
    ├── CTA.tsx             # 問い合わせフォーム
    └── Footer.tsx          # フッター

frontend/app/api/inquiry/
└── route.ts                # 問い合わせAPI
```

#### アクセス方法

開発環境：
```
http://localhost:3000/lp-camper-repair
```

本番環境：
```
https://your-domain.com/lp-camper-repair
```

**注意**: このLPは**お客様（キャンピングカー所有者）向け**のページです。修理工場向けの登録ページは別途 `/lp-partner-recruit` にあります。

---

### キャンピングカー修理パートナー募集LP (`/lp-partner-recruit`)

修理工場・大工・公務店・自動車整備工場・個人職人向けのパートナー募集ランディングページです。専門業者でなくても参画できることを強調し、幅広い業種の方に参加を呼びかけます。

#### 構成セクション（修理工場向け）

1. **ヒーローセクション**
   - キャッチコピー：「キャンピングカー修理ができる業者さん募集！専門業者でなくてもOKです。」
   - CTAボタン：無料でパートナー登録する、まずは話を聞いてみる
   - 統計情報：月間修理依頼数、平均単価、対応エリア

2. **なぜ "非キャンピングカー修理業者" でもできるのか**
   - キャンピングカー修理の多くは住宅設備に似ている
   - 特殊技術が必要なのは全体の20%程度
   - AI診断が一次切り分けしてくれる
   - 施工マニュアルは当社が提供

3. **パートナーになるメリット**
   - 全国から修理依頼が自動で届く
   - 高単価（1件3〜20万円）
   - 原価がほぼかからず利益率が高い
   - キャンピングカー業界は職人不足のブルーオーシャン
   - AIが一次診断→案件化するので現場が楽
   - 面倒なクレーム受付・事務局業務は当社が代行

4. **修理依頼の流れ**
   - 5ステップのフローチャート
   - ユーザー→AI診断→案件通知→見積もり＆修理→売上支払い

5. **パートナー条件**
   - キャンピングカー専門でなくてOK
   - 普通の工具があればOK
   - 個人事業主可
   - 作業スピードより「誠実対応」を重視

6. **料金モデル**
   - 登録費：無料
   - 手数料：売上の10〜20%（修理完了後に支払い）

7. **事例紹介**
   - 大工さんでもできた
   - 車屋さんで年商300万円アップ
   - 公務店が副業的に参入

8. **よくある質問（FAQ）**
   - 専門知識なくてもできますか？
   - 作業できない案件はどうしたら？
   - 自宅でもできますか？
   - 遠方からの依頼は？
   - 個人事業主でも登録できますか？
   - 手数料はいつ支払われますか？

9. **パートナー登録フォーム**
   - 名前、会社名、電話番号、メールアドレス
   - 対応エリア、できる作業、設備・経験の有無
   - APIエンドポイント：後で接続予定

#### 技術仕様

- **フレームワーク**: Next.js 14 (App Router)
- **スタイリング**: TailwindCSS v4
- **デザイン**: 緑系（green-600, green-700, emerald-800）+ 黄色アクセント
- **レスポンシブ**: スマホファースト
- **SEO**: メタタグ、Open Graph、構造化データ（LocalBusiness）

#### ファイル構成

```
frontend/app/lp-partner-recruit/
├── layout.tsx              # SEOメタタグ設定
├── page.tsx                # メインページ
└── components/
    ├── Hero.tsx            # ヒーローセクション
    ├── WhyUs.tsx           # なぜ非キャンピングカー修理業者でもできるのか
    ├── Merits.tsx          # パートナーになるメリット
    ├── Flow.tsx            # 修理依頼の流れ
    ├── Conditions.tsx      # パートナー条件
    ├── Pricing.tsx         # 料金モデル
    ├── Cases.tsx           # 事例紹介
    ├── FAQ.tsx             # よくある質問
    └── PartnerForm.tsx     # パートナー登録フォーム
```

#### アクセス方法

開発環境：
```
http://localhost:3000/lp-partner-recruit
```

本番環境：
```
https://your-domain.com/lp-partner-recruit
```

**注意**: このLPは**修理工場・大工・公務店・自動車整備工場・個人職人向け**のページです。お客様（キャンピングカー所有者）向けのページは `/lp-camper-repair` にあります。

## 📧 メール通知機能の実装方法（Resend）

### 概要

Notionで修理ステータスを更新すると、お客様に自動でメール通知が送信される仕組みです。

**動作フロー：**
1. お客様が修理店に問い合わせ → Notion DBに商談情報が保存
2. 修理工場がNotionでステータスを更新（「診断中」「修理中」「完了」など）
3. システムが自動でお客様にメール通知を送信
4. 修理完了時には支払い案内も自動送信

### Resendを使う理由

- **設定が簡単**: APIキーだけで送信できる
- **高い到達率**: トランザクションメールに強い
- **運用が楽**: シンプルな管理画面

### セットアップ手順

#### 1. Resendアカウントを作成

1. [Resend公式サイト](https://resend.com/)にアクセス
2. サインアップしてダッシュボードへ

#### 2. APIキーを取得

1. Resendダッシュボードで「API Keys」を開く
2. 「Create API Key」で作成
3. **APIキーをコピー**（`re_...` 形式）

#### 3. 送信元（From）を設定

最初は Resend のデフォルト送信元（例: `onboarding@resend.dev`）を使えます。  
独自ドメイン（例: `info@camper-repair.net`）で送る場合は、Resendでドメイン追加→DNS設定→検証を行ってください。

#### 4. 環境変数を設定

`.env`ファイルに以下を追加：

```bash
# Resend設定
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=onboarding@resend.dev
```

#### 5. 本番環境（Railway）に環境変数を設定

1. [Railway Dashboard](https://railway.app)にログイン
2. プロジェクトを選択
3. 「Variables」タブを開く
4. 以下を追加：
   - `RESEND_API_KEY`: ResendのAPIキー
   - `FROM_EMAIL`: 送信元メールアドレス

### 通知タイミング

以下のタイミングで自動的にメール通知が送信されます：

1. **問い合わせ受付時**
   - お客様: 「問い合わせを受け付けました」
   - 修理店: 「新しい問い合わせが届きました」

2. **ステータス更新時**
   - 「診断中」「修理中」などのステータス変更時に通知

3. **修理完了時**
   - 修理完了通知 + 支払い案内（専用口座情報）

4. **評価依頼**
   - 修理完了後、評価フォームへのリンクを送信

### トラブルシューティング

#### メールが届かない場合

1. **Resend APIキーを確認**
   ```bash
   # Railwayの環境変数を確認
   echo $RESEND_API_KEY
   ```

2. **送信元メールアドレスを確認**
   - SendGridで認証済みか確認
   - `.env`の`FROM_EMAIL`が正しいか確認

3. **SendGridのログを確認**
   - SendGridダッシュボード → 「Activity」で送信履歴を確認

#### SMTPフォールバック

SendGridが利用できない場合、自動的にSMTP（Gmail）経由で送信されます。

```bash
# SMTP設定（フォールバック用）
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

**注意**: Gmailの場合、アプリパスワードを使用してください（2段階認証が必要）。

## 📱 LINE通知機能の実装方法

### 概要

ブラウザ版チャットボットでやり取りし、LINEで通知を送る仕組みです。

**動作フロー：**
1. ユーザーがブラウザ版チャットボットで会話
2. LINE Loginでユーザー認証（LINEユーザーIDを取得）
3. ユーザーIDをNotionデータベースに保存
4. イベント発生時（修理完了、ステータス更新など）にLINEで通知送信

### 前提条件

- LINE Developersアカウントが必要
- Messaging APIチャネルを作成（統合チャネル）
- LINE Loginを有効化

### セットアップ手順

#### 1. LINE Developersでチャネル作成

1. [LINE Developers Console](https://developers.line.biz/ja/)にアクセス
2. プロバイダーを作成
3. 「Messaging API」チャネルを作成
4. 以下を取得：
   - Channel ID
   - Channel Secret
   - Channel Access Token

#### 2. LINE Loginを有効化

1. 作成したMessaging APIチャネルの設定画面で「LINE Login」タブを開く
2. 「LINE Loginを利用する」をONにする
3. Callback URLを設定（例: `https://your-domain.com/api/line/login/callback`）

#### 3. 環境変数を設定

`.env`ファイルに以下を追加：

```bash
# LINE通知機能設定
LINE_CHANNEL_ID=your_channel_id
LINE_CHANNEL_SECRET=your_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_access_token
LINE_LOGIN_CALLBACK_URL=https://your-domain.com/api/line/login/callback
```

#### 4. NotionデータベースにLINEユーザーIDフィールドを追加

商談管理DBに以下のフィールドを追加：

- **LINEユーザーID** (Text) - オプション
- **LINE通知許可** (Checkbox) - LINE通知を送るかどうか

### 実装ファイル

#### 1. LINE通知モジュール

`notification/line_notifier.py` - LINE Messaging APIでプッシュメッセージを送信

```python
from notification.line_notifier import LineNotifier

line_notifier = LineNotifier()
line_notifier.send_to_customer(
    line_user_id="U1234567890abcdef...",
    message="修理が完了しました！"
)
```

#### 2. LINE Login実装

`unified_backend_api.py`に以下のエンドポイントを追加：

- `/api/line/login` - LINE認証を開始
- `/api/line/login/callback` - 認証後のコールバック
- `/api/line/status` - ログイン状態を確認

#### 3. Notionから通知を送るエンドポイント

`/api/v1/notify/line` - Notionデータベースから情報を取得してLINE通知を送信

```python
POST /api/v1/notify/line
{
    "deal_id": "DEAL-20241103-001",
    "type": "repair_complete"  # repair_complete, status_update, reminder
}
```

### 使用方法

#### ステップ1: ユーザーがLINE Loginでログイン

1. ブラウザ版チャットボットで「LINEでログイン」ボタンをクリック
2. LINE認証画面でログイン
3. ユーザーIDが自動的にセッションに保存される

#### ステップ2: Botと友だちになる

LINE通知を受け取るには、ユーザーがBotと友だちになる必要があります。

```html
<!-- 友だち追加ボタンを表示 -->
<a href="https://line.me/R/ti/p/@your-bot-id" target="_blank">
    <img src="https://scdn.line-apps.com/n/line_add_friends/btn/ja.png" alt="友だち追加">
</a>
```

#### ステップ3: 商談作成時にLINEユーザーIDを保存

ブラウザ版で問い合わせフォームを送信すると、自動的にLINEユーザーIDがNotionに保存されます。

#### ステップ4: 通知を送信

修理完了やステータス更新時に、NotionデータベースからLINEユーザーIDを取得して通知を送信：

```python
# 修理完了通知の例
deal_manager.update_deal_status(deal_id, "completed")

# LINE通知を送信
requests.post("/api/v1/notify/line", json={
    "deal_id": deal_id,
    "type": "repair_complete"
})
```

### 通知タイプ

以下の通知タイプが利用可能です：

- **repair_complete** - 修理完了通知
- **status_update** - ステータス更新通知
- **reminder** - リマインダー通知
- **custom** - カスタムメッセージ

### 重要な注意点

1. **Botと友だちになっている必要がある**
   - LINE Messaging APIでプッシュメッセージを送るには、ユーザーがBotと友だちになっている必要があります
   - 友だちでない場合、エラーメッセージが返されます

2. **LINE LoginとLINE Messaging APIは別物**
   - LINE Login: ユーザー認証のみ（メッセージ送信不可）
   - LINE Messaging API: メッセージ送信可能（統合チャネルを使用）

3. **メッセージ送信の制限**
   - プッシュメッセージ: ユーザーがBotと友だちになっている必要がある
   - リプライメッセージ: Webhook経由でユーザーがメッセージを送った場合のみ送信可能

### トラブルシューティング

#### エラー: "not a friend"

ユーザーがBotと友だちになっていない場合に発生します。ユーザーにBotと友だちになってもらう必要があります。

#### エラー: "Invalid channel access token"

環境変数`LINE_CHANNEL_ACCESS_TOKEN`が正しく設定されているか確認してください。

#### エラー: "Invalid callback URL"

LINE LoginのCallback URLが正しく設定されているか確認してください。

### 参考資料

- [LINE Developers ドキュメント](https://developers.line.biz/ja/docs/)
- [LINE Messaging API リファレンス](https://developers.line.biz/ja/reference/messaging-api/)
- [LINE Login API リファレンス](https://developers.line.biz/ja/reference/line-login/)

## 📝 開発履歴

### 2026/01/02 - 管理ダッシュボード機能完成

#### ✅ 完了した機能
1. **工場向けダッシュボード** (`/admin/dashboard`)
   - 案件一覧表示（Notion DBから取得）
   - ステータス更新機能（受付/診断中/修理中/完了/キャンセル）
   - コメント追加機能（Notionページに保存）
   - 経過報告送信機能（最大2回まで）

2. **メール通知機能**
   - Resend API統合
   - ステータス更新時の自動メール送信
   - 経過報告メール送信
   - SendGrid/SMTPフォールバック対応

3. **インデント修正**
   - `partner_shop_manager.py` の都道府県フィルタ部分
   - `factory_dashboard_manager.py` のコメント追加部分
   - `email_sender.py` の例外処理部分
   - `unified_backend_api.py` のエアコン診断部分

4. **経過報告機能のバグ修正**
   - `progress_report_count` が None の場合の処理追加
   - 最大2回までの報告制限実装
   - Notion への自動記録

#### 🔧 技術的な修正
- Python 3.9 互換性対応（`str | None` → `Optional[str]`）
- Notion API バリデーションエラー修正
- ステータスマッピング追加（`in_progress ↔ 修理中`）
- Notion Comments API フォールバック実装

#### 📂 プロジェクト構成の変更
- **日本語パス問題の解決**: Next.js 16 の Turbopack が日本語パスで動作しないため、プロジェクトを `C:\next-camper\camper-repair-clean` にコピーして使用
- バックエンド: 元の場所で起動可能
- フロントエンド: 英数字パスから起動推奨

#### ✅ 完了（2026/01/08）
- ✅ メール送信のテスト（Resend APIキー設定完了、送信成功確認）
- ✅ デバッグログの削除（#region agent log部分を削除）
- ✅ Railway への再デプロイ
- ✅ 本番環境でのメール送信テスト（成功確認）

---

## 🎉 今後の予定

- [x] 工場向けダッシュボード実装
- [x] メール通知機能の実装
- [x] LINE通知機能の実装
- [x] メール送信の本番テスト
- [ ] ユーザー認証機能
- [ ] 修理履歴の保存
- [ ] モバイルアプリ対応
- [ ] 画像アップロード機能
- [ ] 多言語対応
- [ ] LPページの問い合わせAPI連携（Notion/SendGrid）

---

**Powered by:**
- 🤖 OpenAI GPT-4
- 📝 Notion API
- 🔍 ChromaDB
- 🚂 Railway
- ⚡ Flask

Made with ❤️ for キャンピングカー enthusiasts
