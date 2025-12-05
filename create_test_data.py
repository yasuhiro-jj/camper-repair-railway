#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フェーズ1：テストデータ作成スクリプト
Factory ManagerとBuilder Managerを使って直接テストデータを登録します
"""

import os
import sys
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def create_test_factories():
    """テスト工場データを作成"""
    print("=" * 60)
    print("🏭 テスト工場データ作成")
    print("=" * 60)
    
    try:
        from data_access.factory_manager import FactoryManager
        
        factory_manager = FactoryManager()
        
        # テスト工場1
        print("\n1. テスト工場1を登録中...")
        factory1 = factory_manager.create_factory(
            name="山田キャンピングカー修理",
            prefecture="岡山県",
            address="岡山県岡山市北区表町1-2-3",
            phone="086-123-4567",
            email="yamada@example.com",
            specialties=["エアコン", "電装系", "サブバッテリー"],
            business_hours="9:00-18:00",
            service_areas=["岡山県全域"],
            status="アクティブ",
            notes="エアコンと電装系に強い工場です"
        )
        print(f"   ✅ 登録成功: {factory1['factory_id']} - {factory1['name']}")
        
        # テスト工場2
        print("\n2. テスト工場2を登録中...")
        factory2 = factory_manager.create_factory(
            name="広島キャンピングカーサービス",
            prefecture="広島県",
            address="広島県広島市中区本通1-4-5",
            phone="082-234-5678",
            email="hiroshima@example.com",
            specialties=["水回り", "FFヒーター", "冷蔵庫"],
            business_hours="8:30-17:30",
            service_areas=["広島県全域", "山口県東部"],
            status="アクティブ",
            notes="水回りとFFヒーターの修理が得意です"
        )
        print(f"   ✅ 登録成功: {factory2['factory_id']} - {factory2['name']}")
        
        # テスト工場3
        print("\n3. テスト工場3を登録中...")
        factory3 = factory_manager.create_factory(
            name="香川キャンピングカー整備",
            prefecture="香川県",
            address="香川県高松市番町2-6-7",
            phone="087-345-6789",
            email="kagawa@example.com",
            specialties=["トイレ", "雨漏り", "車体外装"],
            business_hours="9:00-19:00",
            service_areas=["香川県全域"],
            status="アクティブ",
            total_cases=10,
            completed_cases=8,
            avg_response_time=2.5,
            rating=4.5,
            notes="トイレと雨漏りの修理実績が豊富です"
        )
        print(f"   ✅ 登録成功: {factory3['factory_id']} - {factory3['name']}")
        
        return [factory1, factory2, factory3]
        
    except Exception as e:
        print(f"\n❌ 工場データ作成エラー: {e}")
        import traceback
        traceback.print_exc()
        return []


def create_test_builders():
    """テストビルダーデータを作成"""
    print("\n" + "=" * 60)
    print("🏢 テストビルダーデータ作成")
    print("=" * 60)
    
    try:
        from data_access.builder_manager import BuilderManager
        
        builder_manager = BuilderManager()
        
        # テストビルダー1
        print("\n1. テストビルダー1を登録中...")
        builder1 = builder_manager.create_builder(
            name="岡山キャンピングカー販売",
            prefecture="岡山県",
            address="岡山県岡山市南区新保3-8-9",
            phone="086-987-6543",
            email="okayama-sales@example.com",
            contact_person="田中太郎",
            line_account="https://line.me/R/ti/p/@okayama-camper",
            status="アクティブ",
            notes="岡山県内の主要なキャンピングカー販売店です"
        )
        print(f"   ✅ 登録成功: {builder1['builder_id']} - {builder1['name']}")
        
        # テストビルダー2
        print("\n2. テストビルダー2を登録中...")
        builder2 = builder_manager.create_builder(
            name="広島RVセンター",
            prefecture="広島県",
            address="広島県広島市西区商工センター4-1-2",
            phone="082-876-5432",
            email="hiroshima-rv@example.com",
            contact_person="佐藤花子",
            status="アクティブ",
            total_referrals=5,
            total_deals=3,
            monthly_fee=30000,
            contract_start_date="2025-01-01",
            notes="広島県内のRV専門販売店です"
        )
        print(f"   ✅ 登録成功: {builder2['builder_id']} - {builder2['name']}")
        
        # テストビルダー3
        print("\n3. テストビルダー3を登録中...")
        builder3 = builder_manager.create_builder(
            name="四国キャンピングカー専門店",
            prefecture="香川県",
            address="香川県高松市林町5-3-1",
            phone="087-765-4321",
            email="shikoku-camper@example.com",
            contact_person="鈴木一郎",
            line_account="https://line.me/R/ti/p/@shikoku-camper",
            status="アクティブ",
            total_referrals=8,
            total_deals=6,
            monthly_fee=50000,
            contract_start_date="2024-12-01",
            notes="四国地方のキャンピングカー専門店です"
        )
        print(f"   ✅ 登録成功: {builder3['builder_id']} - {builder3['name']}")
        
        return [builder1, builder2, builder3]
        
    except Exception as e:
        print(f"\n❌ ビルダーデータ作成エラー: {e}")
        import traceback
        traceback.print_exc()
        return []


def verify_data():
    """登録されたデータを確認"""
    print("\n" + "=" * 60)
    print("🔍 登録データ確認")
    print("=" * 60)
    
    try:
        from data_access.factory_manager import FactoryManager
        from data_access.builder_manager import BuilderManager
        
        factory_manager = FactoryManager()
        builder_manager = BuilderManager()
        
        # 工場一覧取得
        print("\n📋 工場一覧:")
        factories = factory_manager.list_factories()
        print(f"   登録数: {len(factories)}件")
        for factory in factories:
            print(f"   - {factory['factory_id']}: {factory['name']} ({factory['prefecture']})")
        
        # ビルダー一覧取得
        print("\n📋 ビルダー一覧:")
        builders = builder_manager.list_builders()
        print(f"   登録数: {len(builders)}件")
        for builder in builders:
            print(f"   - {builder['builder_id']}: {builder['name']} ({builder['prefecture']})")
        
    except Exception as e:
        print(f"\n❌ データ確認エラー: {e}")
        import traceback
        traceback.print_exc()


def main():
    """メイン関数"""
    print("\n" + "=" * 60)
    print("🚀 フェーズ1：テストデータ作成")
    print("=" * 60)
    
    # 環境変数確認
    print("\n🔍 環境変数確認中...")
    required_vars = ["NOTION_API_KEY", "NOTION_FACTORY_DB_ID", "NOTION_BUILDER_DB_ID"]
    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value[:20]}...")
        else:
            print(f"   ❌ {var}: 未設定")
            all_ok = False
    
    if not all_ok:
        print("\n❌ 必須環境変数が設定されていません")
        print("💡 .envファイルに必要な環境変数を設定してください")
        sys.exit(1)
    
    # テスト工場データ作成
    factories = create_test_factories()
    
    # テストビルダーデータ作成
    builders = create_test_builders()
    
    # データ確認
    verify_data()
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 作成結果サマリー")
    print("=" * 60)
    print(f"工場: {len(factories)}件作成")
    print(f"ビルダー: {len(builders)}件作成")
    
    if factories and builders:
        print("\n🎉 テストデータの作成が完了しました！")
        print("\n💡 次のステップ:")
        print("   1. APIエンドポイントでデータを確認:")
        print("      GET http://localhost:5002/api/v1/factories")
        print("      GET http://localhost:5002/api/v1/builders")
        print("   2. Notionでデータベースを確認")
    else:
        print("\n⚠️ 一部のデータ作成に失敗しました")


if __name__ == "__main__":
    main()

