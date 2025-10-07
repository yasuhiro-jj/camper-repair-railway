#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合システムテスト - 最強チャットボット
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

class UnifiedSystemTester:
    def __init__(self):
        self.backend_url = "http://localhost:5002"
        self.frontend_url = "http://localhost:5001"
        self.test_results = []
    
    async def run_all_tests(self):
        """全テストの実行"""
        print("🔧 最強キャンピングカー修理チャットボット - 統合システムテスト")
        print("=" * 60)
        
        tests = [
            ("バックエンドAPI接続テスト", self.test_backend_connection),
            ("統合チャット機能テスト", self.test_unified_chat),
            ("診断機能テスト", self.test_diagnostic),
            ("修理検索機能テスト", self.test_repair_search),
            ("費用見積もり機能テスト", self.test_cost_estimate),
            ("高度機能テスト", self.test_advanced_features),
            ("パフォーマンステスト", self.test_performance)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 {test_name}を実行中...")
            try:
                result = await test_func()
                self.test_results.append({
                    "test_name": test_name,
                    "status": "PASS" if result["success"] else "FAIL",
                    "details": result
                })
                print(f"✅ {test_name}: {'成功' if result['success'] else '失敗'}")
            except Exception as e:
                self.test_results.append({
                    "test_name": test_name,
                    "status": "ERROR",
                    "details": {"error": str(e)}
                })
                print(f"❌ {test_name}: エラー - {e}")
        
        # テスト結果の表示
        self.display_test_results()
    
    async def test_backend_connection(self):
        """バックエンド接続テスト"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/api/unified/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "response_time": response.headers.get("X-Response-Time", "N/A"),
                            "services": data.get("services", {})
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_unified_chat(self):
        """統合チャット機能テスト"""
        test_messages = [
            "バッテリーが上がりません",
            "エアコンが効きません",
            "トイレが詰まりました",
            "雨漏りがします"
        ]
        
        results = []
        for message in test_messages:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.backend_url}/api/unified/chat",
                        json={"message": message, "mode": "chat"},
                        timeout=30
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            results.append({
                                "message": message,
                                "success": True,
                                "response_type": data.get("type"),
                                "has_response": bool(data.get("response"))
                            })
                        else:
                            results.append({
                                "message": message,
                                "success": False,
                                "error": f"HTTP {response.status}"
                            })
            except Exception as e:
                results.append({
                    "message": message,
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        return {
            "success": success_count == len(test_messages),
            "total_tests": len(test_messages),
            "successful_tests": success_count,
            "results": results
        }
    
    async def test_diagnostic(self):
        """診断機能テスト"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/api/unified/diagnostic",
                    json={
                        "symptoms": ["エンジンがかからない", "異音がする"],
                        "additional_info": "朝から動かない"
                    },
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "has_diagnosis": bool(data.get("diagnosis")),
                            "has_symptoms": bool(data.get("symptoms"))
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_repair_search(self):
        """修理検索機能テスト"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/api/unified/search",
                    json={
                        "query": "バッテリー交換",
                        "types": ["rag", "serp", "categories"]
                    },
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "has_rag_results": bool(data.get("results", {}).get("rag")),
                            "has_serp_results": bool(data.get("results", {}).get("serp")),
                            "has_category_results": bool(data.get("results", {}).get("categories"))
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_cost_estimate(self):
        """費用見積もり機能テスト"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/api/unified/chat",
                    json={
                        "message": "エアコン修理の費用を知りたい",
                        "mode": "cost_estimate"
                    },
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "response_type": data.get("type"),
                            "has_cost_info": bool(data.get("cost_info"))
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_advanced_features(self):
        """高度機能テスト"""
        try:
            # 高度機能のテスト（実際の実装では advanced_features.py を使用）
            from advanced_features import AdvancedFeatures
            
            advanced = AdvancedFeatures()
            
            # マルチモーダル入力のテスト
            test_input = {
                "text": "バッテリーが上がりません",
                "image": None,
                "audio": None
            }
            
            result = await advanced.process_multimodal_input(test_input)
            
            return {
                "success": True,
                "has_text_analysis": bool(result.get("text_analysis")),
                "has_integrated_response": bool(result.get("integrated_response"))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_performance(self):
        """パフォーマンステスト"""
        try:
            start_time = time.time()
            
            # 複数のリクエストを並行実行
            tasks = []
            for i in range(5):
                task = self.test_single_request(f"テストメッセージ {i+1}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            successful_requests = sum(1 for r in results if r["success"])
            total_time = end_time - start_time
            
            return {
                "success": successful_requests == len(tasks),
                "total_requests": len(tasks),
                "successful_requests": successful_requests,
                "total_time": total_time,
                "average_time": total_time / len(tasks)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_single_request(self, message):
        """単一リクエストのテスト"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/api/unified/chat",
                    json={"message": message, "mode": "chat"},
                    timeout=30
                ) as response:
                    return {
                        "success": response.status == 200,
                        "status_code": response.status
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def display_test_results(self):
        """テスト結果の表示"""
        print("\n" + "=" * 60)
        print("📊 テスト結果サマリー")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed_tests = sum(1 for r in self.test_results if r["status"] == "FAIL")
        error_tests = sum(1 for r in self.test_results if r["status"] == "ERROR")
        
        print(f"総テスト数: {total_tests}")
        print(f"✅ 成功: {passed_tests}")
        print(f"❌ 失敗: {failed_tests}")
        print(f"⚠️ エラー: {error_tests}")
        print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 詳細結果:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['test_name']}: {result['status']}")
            
            if result["status"] != "PASS" and "error" in result["details"]:
                print(f"   エラー: {result['details']['error']}")
        
        # 推奨事項の表示
        self.display_recommendations()
    
    def display_recommendations(self):
        """推奨事項の表示"""
        print("\n💡 推奨事項:")
        
        failed_tests = [r for r in self.test_results if r["status"] in ["FAIL", "ERROR"]]
        
        if not failed_tests:
            print("🎉 すべてのテストが成功しました！システムは正常に動作しています。")
            return
        
        print("以下の点を確認してください:")
        
        for result in failed_tests:
            if "バックエンド" in result["test_name"]:
                print("- バックエンドAPIが起動しているか確認してください")
                print("- 環境変数が正しく設定されているか確認してください")
            elif "チャット" in result["test_name"]:
                print("- OpenAI APIキーが設定されているか確認してください")
                print("- ネットワーク接続を確認してください")
            elif "診断" in result["test_name"]:
                print("- 診断データが正しく読み込まれているか確認してください")
            elif "検索" in result["test_name"]:
                print("- RAGシステムが正常に動作しているか確認してください")
                print("- SERP APIキーが設定されているか確認してください")

async def main():
    """メイン関数"""
    tester = UnifiedSystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
