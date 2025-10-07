#!/usr/bin/env python
# -*- coding: utf-8 -*-

def get_relevant_blog_links(query):
    """クエリに基づいて関連ブログを返す"""
    query_lower = query.lower()
    
    blog_links = [
        {
            "title": "バッテリー・バッテリーの故障と修理方法",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["バッテリー", "充電", "電圧", "上がり", "始動", "エンジン"]
        },
        {
            "title": "基本修理・キャンピングカー修理の基本",
            "url": "https://camper-repair.net/blog/risk1/",
            "keywords": ["修理", "基本", "手順", "工具", "部品", "故障"]
        },
        {
            "title": "定期点検・定期点検とメンテナンス",
            "url": "https://camper-repair.net/battery-selection/",
            "keywords": ["点検", "メンテナンス", "定期", "予防", "保守", "チェック"]
        },
        {
            "title": "水道ポンプ・給水システムの修理",
            "url": "https://camper-repair.net/blog/water-system/",
            "keywords": ["水道", "ポンプ", "給水", "水", "蛇口", "タンク"]
        },
        {
            "title": "電気系統・配線の修理方法",
            "url": "https://camper-repair.net/blog/electrical/",
            "keywords": ["電気", "配線", "コンセント", "スイッチ", "LED", "照明"]
        },
        {
            "title": "冷蔵庫・家電製品の故障対処",
            "url": "https://camper-repair.net/blog/appliance/",
            "keywords": ["冷蔵庫", "家電", "電化製品", "故障", "動作しない"]
        },
        {
            "title": "ガスシステム・安全確認方法",
            "url": "https://camper-repair.net/blog/gas-system/",
            "keywords": ["ガス", "コンロ", "ヒーター", "安全", "漏れ"]
        },
        {
            "title": "車体・外装の修理とメンテナンス",
            "url": "https://camper-repair.net/blog/body-repair/",
            "keywords": ["車体", "外装", "傷", "錆", "雨漏り", "破損"]
        },
        {
            "title": "キャンピングカーのエアコン取り付け｜あなたに最適なタイプと選び方とは",
            "url": "https://camper-repair.net/blog/air-conditioner2/",
            "keywords": [
                "キャンピングカー",
                "エアコン取り付け",
                "車載エアコン",
                "ポータブルエアコン",
                "セパレートエアコン",
                "ルーフエアコン",
                "窓用エアコン",
                "12Vエアコン",
                "DC電源エアコン",
                "走行中エアコン",
                "停車中エアコン",
                "電源容量",
                "消費電力",
                "快適性",
                "エアコン選びのポイント"
            ]
        },
        {
            "title": "キャンピングカーに最適なエアコンとは？家庭用・12V・ポータブルの違いを解説",
            "url": "https://camper-repair.net/blog/air-condituioner2/",
            "keywords": [
                "キャンピングカー",
                "最適なエアコン",
                "家庭用エアコン",
                "12Vエアコン",
                "ポータブルエアコン",
                "車載エアコン",
                "後付けエアコン",
                "冷却性能",
                "消費電力",
                "電源容量",
                "発電機対応",
                "サブバッテリー",
                "取り付け方法",
                "エアコン比較",
                "選び方のポイント"
            ]
        },
        {
            "title": "キャンピングカーのエアコン後付け費用や機種の選び方ガイド",
            "url": "https://camper-repair.net/blog/air-conditioner1/",
            "keywords": [
                "キャンピングカー",
                "エアコン後付け",
                "取り付け費用",
                "エアコン工賃",
                "設置料金",
                "車載エアコン",
                "12Vエアコン",
                "家庭用エアコン",
                "ポータブルエアコン",
                "ルーフエアコン",
                "窓用エアコン",
                "おすすめ機種",
                "コスト比較",
                "取り付け業者",
                "選び方ガイド"
            ]
        }
    ]
    
    relevant_blogs = []
    
    # エアコン関連のキーワードマッピング（より柔軟な検索のため）
    aircon_keywords = ["エアコン", "aircon", "air con", "冷房", "暖房", "クーラー", "冷却", "空調"]
    
    for blog in blog_links:
        score = 0
        
        # エアコン関連の特別処理
        if any(keyword in query_lower for keyword in aircon_keywords):
            # エアコン関連ブログかチェック
            if "エアコン" in blog["title"] or any("エアコン" in keyword for keyword in blog["keywords"]):
                score += 10  # 高いスコアを付与
        
        # 通常のキーワードマッチング
        for keyword in blog["keywords"]:
            keyword_lower = keyword.lower()
            if keyword_lower in query_lower:
                score += 2  # 通常のキーワードマッチ
            elif any(part in query_lower for part in keyword_lower.split() if len(part) > 2):
                score += 1  # 部分マッチ
        
        # タイトル内のキーワードもチェック
        title_lower = blog["title"].lower()
        for keyword in query_lower.split():
            if len(keyword) > 2 and keyword in title_lower:
                score += 1
        
        if score > 0:
            relevant_blogs.append((blog, score))
    
    relevant_blogs.sort(key=lambda x: x[1], reverse=True)
    return [blog for blog, score in relevant_blogs[:3]]

def test_rag():
    """RAGの動作をテスト"""
    print("=== RAG（Retrieval-Augmented Generation）テスト ===\n")
    
    # テストクエリ
    test_queries = [
        "バッテリーが上がってエンジンが始動しない",
        "水道ポンプが動かない",
        "ガスコンロに火がつかない",
        "冷蔵庫が冷えない",
        "電気配線の問題",
        "車体の傷の修理",
        "エアコンが効かない",
        "エアコン取り付け",
        "冷房が効かない",
        "クーラー故障"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"テスト {i}: {query}")
        print("-" * 50)
        
        # 関連ブログを取得
        relevant_blogs = get_relevant_blog_links(query)
        
        if relevant_blogs:
            print("関連ブログが見つかりました:")
            for j, blog in enumerate(relevant_blogs, 1):
                print(f"  {j}. {blog['title']}")
                print(f"     URL: {blog['url']}")
                print(f"     キーワード: {', '.join(blog['keywords'])}")
                print()
        else:
            print("関連ブログが見つかりませんでした。")
        
        print("=" * 60)
        print()

if __name__ == "__main__":
    test_rag()
