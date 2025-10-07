#!/usr/bin/env python3
"""
Anaconda環境用クイックセットアップスクリプト
"""

import os
import sys
import subprocess
import platform

def run_command(command, description=""):
    """コマンドを実行"""
    print(f"🔄 {description}")
    print(f"実行中: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - 失敗")
        print(f"エラー: {e.stderr}")
        return False

def check_conda():
    """condaが利用可能かチェック"""
    try:
        result = subprocess.run("conda --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ conda: {result.stdout.strip()}")
            return True
        else:
            print("❌ condaが見つかりません")
            return False
    except:
        print("❌ condaが見つかりません")
        return False

def create_conda_environment():
    """conda環境を作成"""
    print("\n🐍 conda環境を作成中...")
    
    # 環境が既に存在するかチェック
    result = subprocess.run("conda env list", shell=True, capture_output=True, text=True)
    if "camper-repair" in result.stdout:
        print("⚠️ 環境 'camper-repair' は既に存在します")
        choice = input("既存の環境を削除して再作成しますか？ (y/n): ")
        if choice.lower() == 'y':
            run_command("conda env remove -n camper-repair -y", "既存環境の削除")
        else:
            print("既存の環境を使用します")
            return True
    
    # 新しい環境を作成
    if run_command("conda env create -f environment.yml", "conda環境の作成"):
        return True
    else:
        # フォールバック: 手動で環境を作成
        print("📦 フォールバック: 手動で環境を作成中...")
        commands = [
            ("conda create -n camper-repair python=3.9 -y", "Python環境の作成"),
            ("conda activate camper-repair && pip install -r requirements.txt", "依存関係のインストール")
        ]
        
        for cmd, desc in commands:
            if not run_command(cmd, desc):
                return False
        
        return True

def setup_environment_variables():
    """環境変数を設定"""
    print("\n⚙️ 環境変数を設定中...")
    
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ {env_file}ファイルが既に存在します")
        return True
    
    # .envファイルを作成
    env_content = """# OpenAI API設定
OPENAI_API_KEY=your_openai_api_key_here

# Notion API設定（オプション）
NOTION_API_KEY=your_notion_api_key_here
NODE_DB_ID=your_notion_node_db_id
CASE_DB_ID=your_notion_case_db_id
ITEM_DB_ID=your_notion_item_db_id

# その他の設定
SERP_API_KEY=your_serp_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=default
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✅ {env_file}ファイルが作成されました")
        print("⚠️  .envファイルを編集してAPIキーを設定してください")
        return True
    except Exception as e:
        print(f"❌ {env_file}ファイルの作成に失敗: {e}")
        return False

def test_installation():
    """インストールをテスト"""
    print("\n🧪 インストールをテスト中...")
    
    # conda環境をアクティベート
    if platform.system() == "Windows":
        activate_cmd = "conda activate camper-repair"
    else:
        activate_cmd = "source activate camper-repair"
    
    test_commands = [
        f"{activate_cmd} && python -c \"import streamlit; print('✅ Streamlit:', streamlit.__version__)\"",
        f"{activate_cmd} && python -c \"import langchain; print('✅ LangChain:', langchain.__version__)\"",
        f"{activate_cmd} && python -c \"import openai; print('✅ OpenAI:', openai.__version__)\"",
        f"{activate_cmd} && python -c \"import flask; print('✅ Flask:', flask.__version__)\""
    ]
    
    success_count = 0
    for cmd in test_commands:
        if run_command(cmd, "パッケージテスト"):
            success_count += 1
    
    return success_count == len(test_commands)

def main():
    """メイン関数"""
    print("🔧 キャンピングカー修理AIチャットアプリ")
    print("Anaconda環境用クイックセットアップ")
    print("=" * 50)
    
    # condaの確認
    if not check_conda():
        print("\n❌ condaがインストールされていません")
        print("Anacondaをインストールしてください: https://www.anaconda.com/")
        return False
    
    # プロジェクトディレクトリに移動
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    print(f"📁 プロジェクトディレクトリ: {project_dir}")
    
    # conda環境を作成
    if not create_conda_environment():
        print("\n❌ conda環境の作成に失敗しました")
        return False
    
    # 環境変数を設定
    if not setup_environment_variables():
        print("\n❌ 環境変数の設定に失敗しました")
        return False
    
    # インストールをテスト
    if not test_installation():
        print("\n❌ インストールテストに失敗しました")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 セットアップが完了しました！")
    print("\n📋 次のステップ:")
    print("1. .envファイルを編集してAPIキーを設定")
    print("2. 以下のコマンドでアプリを起動:")
    print("   conda activate camper-repair")
    print("   python app.py")
    print("\n📱 ブラウザで http://localhost:5000 にアクセス")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
