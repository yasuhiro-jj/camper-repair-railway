# 🔒 セキュリティ設定ガイド

## ⚠️ 重要なセキュリティ注意事項

**APIキーは絶対にコードに直接記載しないでください！**
- GitHubなどの公開リポジトリにアップロードされる可能性があります
- 悪意のある第三者に悪用されるリスクがあります
- アカウントの不正利用につながる可能性があります

## 🛡️ 推奨設定方法

### 方法1: .envファイル（推奨）

1. **プロジェクトルートに`.env`ファイルを作成**
   ```bash
   # .envファイル
   OPENAI_API_KEY=your_actual_api_key_here
   NOTION_API_KEY=your_notion_token_here
   ```

2. **`.gitignore`に`.env`を追加**
   ```bash
   # .gitignore
   .env
   *.env
   ```

3. **アプリケーションを再起動**

### 方法2: 環境変数

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your_actual_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=your_actual_api_key_here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="your_actual_api_key_here"
```

### 方法3: Streamlitシークレット

1. **`.streamlit/secrets.toml`ファイルを作成**
   ```toml
   # .streamlit/secrets.toml
   OPENAI_API_KEY = "your_actual_api_key_here"
   NOTION_API_KEY = "your_notion_token_here"
   ```

2. **`.gitignore`に追加**
   ```bash
   # .gitignore
   .streamlit/secrets.toml
   ```

## 🔍 セキュリティチェックリスト

- [ ] APIキーがコードに直接記載されていない
- [ ] `.env`ファイルが`.gitignore`に含まれている
- [ ] `secrets.toml`ファイルが`.gitignore`に含まれている
- [ ] 環境変数が適切に設定されている
- [ ] 不要なAPIキーが削除されている

## 🚨 トラブルシューティング

### "OpenAI APIキーが設定されていません"エラー

1. **環境変数の確認**
   ```python
   import os
   print(os.getenv("OPENAI_API_KEY"))
   ```

2. **.envファイルの確認**
   - ファイルが正しい場所にあるか
   - ファイル名が正確か（`.env`）
   - 内容が正しい形式か

3. **Streamlitシークレットの確認**
   ```python
   import streamlit as st
   print(st.secrets.get("OPENAI_API_KEY"))
   ```

## 📚 参考資料

- [OpenAI API ドキュメント](https://platform.openai.com/docs/api-keys)
- [Streamlit シークレット管理](https://docs.streamlit.io/library/advanced-features/secrets-management)
- [Python-dotenv ドキュメント](https://pypi.org/project/python-dotenv/)

## 🆘 緊急時の対応

APIキーが漏洩した場合：

1. **即座にAPIキーを無効化**
   - OpenAIダッシュボードでキーを削除
   - 新しいAPIキーを生成

2. **漏洩箇所の特定**
   - GitHub履歴の確認
   - ログファイルの確認

3. **再発防止策の実施**
   - セキュリティ設定の見直し
   - チームメンバーへの教育

---

**セキュリティは常に最優先事項です！**
