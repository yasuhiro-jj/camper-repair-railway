#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NotionDBにすべての診断データを一括で作成するスクリプト
診断ノード、修理ケース、部品・工具を順番に作成
"""

import os
import sys
import time

def main():
    """メイン処理"""
    print("🚐 キャンピングカー診断システムの完全構築を開始します...")
    print("=" * 60)
    
    # 必要なスクリプトの存在確認
    required_scripts = [
        "create_diagnostic_nodes.py",
        "create_repair_cases.py", 
        "create_items.py"
    ]
    
    missing_scripts = []
    for script in required_scripts:
        if not os.path.exists(script):
            missing_scripts.append(script)
    
    if missing_scripts:
        print("❌ 以下のスクリプトが見つかりません:")
        for script in missing_scripts:
            print(f"   • {script}")
        print("\n💡 必要なスクリプトを作成してから再実行してください。")
        return
    
    print("✅ 必要なスクリプトが確認できました")
    print("\n📋 実行予定:")
    print("1. 診断ノードの作成")
    print("2. 修理ケースの作成") 
    print("3. 部品・工具データの作成")
    print("4. 完了確認")
    
    # 実行確認
    print("\n" + "=" * 60)
    confirm = input("🚀 診断データの作成を開始しますか？ (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes', 'はい']:
        print("❌ 実行をキャンセルしました")
        return
    
    print("\n🚀 診断データの作成を開始します...")
    print("=" * 60)
    
    # 1. 診断ノードの作成
    print("\n🔍 ステップ1: 診断ノードの作成")
    print("-" * 40)
    
    try:
        # 方法1: 直接インポートして実行（推奨）
        print("📝 診断ノード作成スクリプトを直接実行中...")
        import create_diagnostic_nodes
        create_diagnostic_nodes.main()
        print("✅ 診断ノードの作成が完了しました")
        
    except ImportError:
        # 方法2: subprocessで実行（フォールバック）
        print("📝 subprocessで診断ノード作成スクリプトを実行中...")
        import subprocess
        # エンコーディングを指定して実行
        result = subprocess.run([sys.executable, "create_diagnostic_nodes.py"], 
                              capture_output=True, text=True, encoding='cp932')
        
        if result.returncode == 0:
            print("✅ 診断ノードの作成が完了しました")
        else:
            print("❌ 診断ノードの作成に失敗しました")
            print(f"エラー: {result.stderr}")
            return
    except Exception as e:
        print(f"❌ 診断ノード作成スクリプトの実行に失敗: {str(e)}")
        return
    
    print("\n" + "=" * 60)
    input("⏸️ 診断ノードの作成が完了しました。Enterキーを押して次のステップに進んでください...")
    
    # 2. 修理ケースの作成
    print("\n🔧 ステップ2: 修理ケースの作成")
    print("-" * 40)
    
    try:
        # 方法1: 直接インポートして実行（推奨）
        print("📝 修理ケース作成スクリプトを直接実行中...")
        import create_repair_cases
        create_repair_cases.main()
        print("✅ 修理ケースの作成が完了しました")
        
    except ImportError:
        # 方法2: subprocessで実行（フォールバック）
        print("📝 subprocessで修理ケース作成スクリプトを実行中...")
        result = subprocess.run([sys.executable, "create_repair_cases.py"], 
                              capture_output=True, text=True, encoding='cp932')
        
        if result.returncode == 0:
            print("✅ 修理ケースの作成が完了しました")
        else:
            print("❌ 修理ケースの作成に失敗しました")
            print(f"エラー: {result.stderr}")
            return
    except Exception as e:
        print(f"❌ 修理ケース作成スクリプトの実行に失敗: {str(e)}")
        return
    
    print("\n" + "=" * 60)
    input("⏸️ 修理ケースの作成が完了しました。Enterキーを押して次のステップに進んでください...")
    
    # 3. 部品・工具データの作成
    print("\n🛠️ ステップ3: 部品・工具データの作成")
    print("-" * 40)
    
    try:
        # 方法1: 直接インポートして実行（推奨）
        print("📝 部品・工具作成スクリプトを直接実行中...")
        import create_items
        create_items.main()
        print("✅ 部品・工具データの作成が完了しました")
        
    except ImportError:
        # 方法2: subprocessで実行（フォールバック）
        print("📝 subprocessで部品・工具作成スクリプトを実行中...")
        result = subprocess.run([sys.executable, "create_items.py"], 
                              capture_output=True, text=True, encoding='cp932')
        
        if result.returncode == 0:
            print("✅ 部品・工具データの作成が完了しました")
        else:
            print("❌ 部品・工具データの作成に失敗しました")
            print(f"エラー: {result.stderr}")
            return
    except Exception as e:
        print(f"❌ 部品・工具作成スクリプトの実行に失敗: {str(e)}")
        return
    
    # 完了確認
    print("\n" + "=" * 60)
    print("🎉 すべての診断データの作成が完了しました！")
    print("=" * 60)
    
    print("\n📊 作成されたデータ:")
    print("• 診断ノード: 20件（開始ノード10件、詳細ノード10件）")
    print("• 修理ケース: 10件（各カテゴリ別）")
    print("• 部品・工具: 50件以上（部品・工具別）")
    
    print("\n💡 次のステップ:")
    print("1. Streamlitアプリを再起動")
    print("2. 対話式診断をテスト")
    print("3. 実際のデータベースからの診断を確認")
    
    print("\n🚀 診断システムの準備が整いました！")
    print("対話式診断で専門的で正確な診断が可能になります。")

if __name__ == "__main__":
    main()
