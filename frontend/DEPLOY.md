# 🚀 Figmaのように共有する方法

## 方法1: Vercelにデプロイ（推奨・無料）

FigmaのようにオンラインでURLを共有できます。

### 手順

1. **Vercelアカウントを作成**
   - https://vercel.com にアクセス
   - GitHubアカウントでサインアップ（推奨）

2. **プロジェクトをデプロイ**
   - Vercelダッシュボードで「New Project」をクリック
   - GitHubリポジトリを選択（または手動でアップロード）
   - Root Directory: `frontend` を指定
   - Framework Preset: `Next.js` を選択
   - 「Deploy」をクリック

3. **URLを共有**
   - デプロイ完了後、`https://your-project.vercel.app/lp-partner-recruit` のURLが生成されます
   - このURLを誰とでも共有できます！

### メリット
- ✅ 無料で利用可能
- ✅ 自動的にHTTPS対応
- ✅ 世界中からアクセス可能
- ✅ 更新すると自動で再デプロイ
- ✅ FigmaのようにURLを共有するだけ

---

## 方法2: ローカルネットワークで共有

同じWi-Fiに接続している人と共有する場合。

### 手順

1. **開発サーバーを起動**
   ```bash
   cd frontend
   npm run dev
   ```

2. **IPアドレスを確認**
   - Windows: `ipconfig` を実行
   - Mac/Linux: `ifconfig` を実行
   - 例: `192.168.1.100`

3. **URLを共有**
   - `http://192.168.1.100:3000/lp-partner-recruit`
   - 同じWi-Fiに接続している人ならアクセス可能

---

## 方法3: ngrokで一時的に公開（無料）

インターネット経由で一時的に共有する場合。

### 手順

1. **ngrokをインストール**
   - https://ngrok.com/download からダウンロード

2. **開発サーバーを起動**
   ```bash
   cd frontend
   npm run dev
   ```

3. **ngrokでトンネルを作成**
   ```bash
   ngrok http 3000
   ```

4. **生成されたURLを共有**
   - 例: `https://abc123.ngrok.io/lp-partner-recruit`
   - 無料プランではURLが変わる場合があります

---

## 推奨: Vercelデプロイ

最も簡単で安定しているのは**Vercelへのデプロイ**です。
FigmaのようにURLを共有するだけで、誰でもアクセスできます！



