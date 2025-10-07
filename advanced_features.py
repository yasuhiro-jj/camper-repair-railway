#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高度な機能モジュール - 最強チャットボット用
画像認識、音声処理、予測分析、学習機能など
"""

import os
import json
import base64
import io
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import asyncio
import aiohttp

# AI/ML ライブラリ
try:
    import cv2
    import PIL.Image
    import whisper
    import torch
    from transformers import pipeline, AutoTokenizer, AutoModel
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False

try:
    import librosa
    import soundfile as sf
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False

# === 画像認識機能 ===
class ImageAnalyzer:
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """画像認識モデルの読み込み"""
        if not IMAGE_PROCESSING_AVAILABLE:
            return
        
        try:
            # 事前訓練済みモデルの読み込み
            self.model = pipeline("image-classification", 
                                model="microsoft/resnet-50",
                                device=0 if torch.cuda.is_available() else -1)
        except Exception as e:
            print(f"画像認識モデルの読み込みエラー: {e}")
            self.model = None
    
    async def analyze_repair_image(self, image_data: str) -> Dict[str, Any]:
        """修理関連画像の分析"""
        try:
            if not self.model:
                return {"error": "画像認識モデルが利用できません"}
            
            # Base64デコード
            image_bytes = base64.b64decode(image_data)
            image = PIL.Image.open(io.BytesIO(image_bytes))
            
            # 画像分類
            results = self.model(image)
            
            # 修理関連の分析
            repair_analysis = self.analyze_repair_components(results)
            
            return {
                "classification": results,
                "repair_analysis": repair_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"画像分析エラー: {e}"}
    
    def analyze_repair_components(self, classification_results: List[Dict]) -> Dict[str, Any]:
        """修理部品の分析"""
        repair_keywords = [
            "battery", "electrical", "engine", "motor", "pump", "valve",
            "pipe", "tube", "connector", "wire", "cable", "switch"
        ]
        
        relevant_items = []
        for result in classification_results:
            if any(keyword in result["label"].lower() for keyword in repair_keywords):
                relevant_items.append({
                    "component": result["label"],
                    "confidence": result["score"],
                    "repair_relevance": "high" if result["score"] > 0.7 else "medium"
                })
        
        return {
            "relevant_components": relevant_items,
            "repair_priority": "high" if len(relevant_items) > 0 else "low"
        }

# === 音声処理機能 ===
class AudioProcessor:
    def __init__(self):
        self.whisper_model = None
        self.load_model()
    
    def load_model(self):
        """音声認識モデルの読み込み"""
        if not AUDIO_PROCESSING_AVAILABLE:
            return
        
        try:
            self.whisper_model = whisper.load_model("base")
        except Exception as e:
            print(f"音声認識モデルの読み込みエラー: {e}")
            self.whisper_model = None
    
    async def transcribe_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """音声の文字起こし"""
        try:
            if not self.whisper_model:
                return {"error": "音声認識モデルが利用できません"}
            
            # 音声ファイルの保存
            temp_file = f"temp_audio_{datetime.now().timestamp()}.wav"
            with open(temp_file, "wb") as f:
                f.write(audio_data)
            
            # 文字起こし
            result = self.whisper_model.transcribe(temp_file)
            
            # 一時ファイルの削除
            os.remove(temp_file)
            
            return {
                "transcription": result["text"],
                "language": result["language"],
                "segments": result.get("segments", []),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"音声文字起こしエラー: {e}"}
    
    async def analyze_audio_quality(self, audio_data: bytes) -> Dict[str, Any]:
        """音声品質の分析"""
        try:
            # 音声データの読み込み
            audio_array, sample_rate = librosa.load(io.BytesIO(audio_data))
            
            # 音声品質の分析
            quality_metrics = {
                "sample_rate": sample_rate,
                "duration": len(audio_array) / sample_rate,
                "rms_energy": float(np.sqrt(np.mean(audio_array**2))),
                "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(audio_array))),
                "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(audio_array, sr=sample_rate)))
            }
            
            # 品質評価
            quality_score = self.calculate_audio_quality_score(quality_metrics)
            
            return {
                "metrics": quality_metrics,
                "quality_score": quality_score,
                "recommendations": self.get_audio_quality_recommendations(quality_score)
            }
            
        except Exception as e:
            return {"error": f"音声品質分析エラー: {e}"}
    
    def calculate_audio_quality_score(self, metrics: Dict[str, float]) -> float:
        """音声品質スコアの計算"""
        score = 0.0
        
        # サンプルレートの評価
        if metrics["sample_rate"] >= 44100:
            score += 0.3
        elif metrics["sample_rate"] >= 22050:
            score += 0.2
        
        # RMSエネルギーの評価
        if 0.01 <= metrics["rms_energy"] <= 0.5:
            score += 0.3
        elif 0.005 <= metrics["rms_energy"] <= 0.8:
            score += 0.2
        
        # ゼロクロッシングレートの評価
        if 0.01 <= metrics["zero_crossing_rate"] <= 0.1:
            score += 0.2
        
        # スペクトラルセントロイドの評価
        if 1000 <= metrics["spectral_centroid"] <= 4000:
            score += 0.2
        
        return min(score, 1.0)
    
    def get_audio_quality_recommendations(self, quality_score: float) -> List[str]:
        """音声品質改善の推奨事項"""
        recommendations = []
        
        if quality_score < 0.5:
            recommendations.append("マイクを近づけて話してください")
            recommendations.append("静かな環境で録音してください")
            recommendations.append("より高品質なマイクの使用を検討してください")
        elif quality_score < 0.8:
            recommendations.append("音声の品質は良好です")
            recommendations.append("より詳細な説明を追加してください")
        
        return recommendations

# === 予測分析機能 ===
class PredictiveAnalyzer:
    def __init__(self):
        self.repair_patterns = {}
        self.load_historical_data()
    
    def load_historical_data(self):
        """履歴データの読み込み"""
        try:
            # 修理履歴データの読み込み（実際の実装ではデータベースから取得）
            self.repair_patterns = {
                "seasonal_patterns": {
                    "春": ["雨漏り", "窓の開閉不良"],
                    "夏": ["エアコン故障", "バッテリー上がり"],
                    "秋": ["ヒーター故障", "給湯器故障"],
                    "冬": ["凍結", "配管破裂"]
                },
                "age_patterns": {
                    "0-2年": ["初期不良", "設定ミス"],
                    "3-5年": ["消耗品交換", "メンテナンス"],
                    "6-10年": ["部品劣化", "配線問題"],
                    "10年以上": ["全面点検", "部品交換"]
                },
                "usage_patterns": {
                    "高頻度使用": ["早期劣化", "消耗品交換"],
                    "低頻度使用": ["腐食", "配線断線"],
                    "長期保管": ["バッテリー劣化", "シール劣化"]
                }
            }
        except Exception as e:
            print(f"履歴データの読み込みエラー: {e}")
    
    async def predict_repair_needs(self, vehicle_info: Dict[str, Any]) -> Dict[str, Any]:
        """修理需要の予測"""
        try:
            predictions = {
                "immediate_needs": [],
                "short_term_needs": [],
                "long_term_needs": [],
                "preventive_measures": []
            }
            
            # 季節パターンの分析
            current_season = self.get_current_season()
            if current_season in self.repair_patterns["seasonal_patterns"]:
                predictions["immediate_needs"].extend(
                    self.repair_patterns["seasonal_patterns"][current_season]
                )
            
            # 年齢パターンの分析
            vehicle_age = vehicle_info.get("age", 0)
            age_category = self.get_age_category(vehicle_age)
            if age_category in self.repair_patterns["age_patterns"]:
                predictions["short_term_needs"].extend(
                    self.repair_patterns["age_patterns"][age_category]
                )
            
            # 使用パターンの分析
            usage_pattern = vehicle_info.get("usage_pattern", "normal")
            if usage_pattern in self.repair_patterns["usage_patterns"]:
                predictions["long_term_needs"].extend(
                    self.repair_patterns["usage_patterns"][usage_pattern]
                )
            
            # 予防措置の提案
            predictions["preventive_measures"] = self.get_preventive_measures(vehicle_info)
            
            return {
                "predictions": predictions,
                "confidence": self.calculate_prediction_confidence(vehicle_info),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"予測分析エラー: {e}"}
    
    def get_current_season(self) -> str:
        """現在の季節を取得"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "春"
        elif month in [6, 7, 8]:
            return "夏"
        elif month in [9, 10, 11]:
            return "秋"
        else:
            return "冬"
    
    def get_age_category(self, age: int) -> str:
        """年齢カテゴリの取得"""
        if age <= 2:
            return "0-2年"
        elif age <= 5:
            return "3-5年"
        elif age <= 10:
            return "6-10年"
        else:
            return "10年以上"
    
    def get_preventive_measures(self, vehicle_info: Dict[str, Any]) -> List[str]:
        """予防措置の提案"""
        measures = []
        
        # 基本的な予防措置
        measures.extend([
            "定期的な点検",
            "清掃・メンテナンス",
            "適切な保管環境の確保"
        ])
        
        # 車両情報に基づく予防措置
        if vehicle_info.get("usage_pattern") == "高頻度使用":
            measures.extend([
                "消耗品の早期交換",
                "定期的なオイル交換",
                "配線の点検"
            ])
        elif vehicle_info.get("usage_pattern") == "低頻度使用":
            measures.extend([
                "長期保管時のバッテリー管理",
                "防錆処理",
                "定期的な動作確認"
            ])
        
        return measures
    
    def calculate_prediction_confidence(self, vehicle_info: Dict[str, Any]) -> float:
        """予測信頼度の計算"""
        confidence = 0.5  # ベース信頼度
        
        # 情報の完全性による調整
        if vehicle_info.get("age") is not None:
            confidence += 0.2
        if vehicle_info.get("usage_pattern"):
            confidence += 0.2
        if vehicle_info.get("maintenance_history"):
            confidence += 0.1
        
        return min(confidence, 1.0)

# === 学習機能 ===
class LearningSystem:
    def __init__(self):
        self.knowledge_base = {}
        self.user_feedback = []
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """知識ベースの読み込み"""
        try:
            # 既存の知識ベースの読み込み
            if os.path.exists("knowledge_base.json"):
                with open("knowledge_base.json", "r", encoding="utf-8") as f:
                    self.knowledge_base = json.load(f)
        except Exception as e:
            print(f"知識ベースの読み込みエラー: {e}")
            self.knowledge_base = {}
    
    async def learn_from_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """インタラクションからの学習"""
        try:
            # インタラクションデータの保存
            self.user_feedback.append({
                "timestamp": datetime.now().isoformat(),
                "interaction": interaction
            })
            
            # 知識の更新
            updated_knowledge = self.update_knowledge_base(interaction)
            
            # 学習結果の保存
            await self.save_learning_results(updated_knowledge)
            
            return {
                "learning_success": True,
                "updated_knowledge": updated_knowledge,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"学習エラー: {e}"}
    
    def update_knowledge_base(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """知識ベースの更新"""
        updated_knowledge = {}
        
        # 問題解決パターンの学習
        if interaction.get("problem_solved"):
            problem_type = interaction.get("problem_type")
            solution = interaction.get("solution")
            
            if problem_type not in self.knowledge_base:
                self.knowledge_base[problem_type] = []
            
            self.knowledge_base[problem_type].append({
                "solution": solution,
                "effectiveness": interaction.get("effectiveness", 0.5),
                "timestamp": datetime.now().isoformat()
            })
            
            updated_knowledge[problem_type] = self.knowledge_base[problem_type]
        
        return updated_knowledge
    
    async def save_learning_results(self, updated_knowledge: Dict[str, Any]):
        """学習結果の保存"""
        try:
            # 知識ベースの保存
            with open("knowledge_base.json", "w", encoding="utf-8") as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            
            # フィードバックの保存
            with open("user_feedback.json", "w", encoding="utf-8") as f:
                json.dump(self.user_feedback, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"学習結果の保存エラー: {e}")
    
    async def get_learned_solutions(self, problem_type: str) -> List[Dict[str, Any]]:
        """学習済みソリューションの取得"""
        try:
            if problem_type in self.knowledge_base:
                solutions = self.knowledge_base[problem_type]
                # 効果性でソート
                solutions.sort(key=lambda x: x.get("effectiveness", 0), reverse=True)
                return solutions[:5]  # 上位5件を返す
            else:
                return []
        except Exception as e:
            print(f"学習済みソリューション取得エラー: {e}")
            return []

# === 統合高度機能クラス ===
class AdvancedFeatures:
    def __init__(self):
        self.image_analyzer = ImageAnalyzer()
        self.audio_processor = AudioProcessor()
        self.predictive_analyzer = PredictiveAnalyzer()
        self.learning_system = LearningSystem()
    
    async def process_multimodal_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """マルチモーダル入力の処理"""
        try:
            results = {
                "text_analysis": None,
                "image_analysis": None,
                "audio_analysis": None,
                "integrated_response": None
            }
            
            # テキスト分析
            if input_data.get("text"):
                results["text_analysis"] = await self.analyze_text(input_data["text"])
            
            # 画像分析
            if input_data.get("image"):
                results["image_analysis"] = await self.image_analyzer.analyze_repair_image(input_data["image"])
            
            # 音声分析
            if input_data.get("audio"):
                results["audio_analysis"] = await self.audio_processor.transcribe_audio(input_data["audio"])
            
            # 統合レスポンスの生成
            results["integrated_response"] = await self.generate_integrated_response(results)
            
            return results
            
        except Exception as e:
            return {"error": f"マルチモーダル処理エラー: {e}"}
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """テキスト分析"""
        try:
            # 感情分析、キーワード抽出、意図分析など
            analysis = {
                "sentiment": "neutral",  # 実際の実装では感情分析を実行
                "keywords": self.extract_keywords(text),
                "intent": self.analyze_intent(text),
                "urgency": self.assess_urgency(text)
            }
            return analysis
        except Exception as e:
            return {"error": f"テキスト分析エラー: {e}"}
    
    def extract_keywords(self, text: str) -> List[str]:
        """キーワード抽出"""
        # 簡単なキーワード抽出（実際の実装ではより高度な手法を使用）
        repair_keywords = [
            "バッテリー", "エアコン", "トイレ", "雨漏り", "エンジン",
            "故障", "修理", "交換", "点検", "メンテナンス"
        ]
        
        found_keywords = []
        for keyword in repair_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def analyze_intent(self, text: str) -> str:
        """意図分析"""
        if any(word in text for word in ["故障", "壊れた", "動かない"]):
            return "troubleshooting"
        elif any(word in text for word in ["修理", "直したい", "交換"]):
            return "repair"
        elif any(word in text for word in ["費用", "値段", "いくら"]):
            return "cost_inquiry"
        else:
            return "general_inquiry"
    
    def assess_urgency(self, text: str) -> str:
        """緊急度の評価"""
        urgent_keywords = ["緊急", "すぐに", "今すぐ", "至急"]
        if any(keyword in text for keyword in urgent_keywords):
            return "high"
        elif any(word in text for word in ["故障", "壊れた"]):
            return "medium"
        else:
            return "low"
    
    async def generate_integrated_response(self, analysis_results: Dict[str, Any]) -> str:
        """統合レスポンスの生成"""
        try:
            response_parts = []
            
            # テキスト分析結果の統合
            if analysis_results.get("text_analysis"):
                text_analysis = analysis_results["text_analysis"]
                if text_analysis.get("urgency") == "high":
                    response_parts.append("🚨 緊急度の高い問題として認識しました。")
            
            # 画像分析結果の統合
            if analysis_results.get("image_analysis"):
                image_analysis = analysis_results["image_analysis"]
                if image_analysis.get("repair_analysis", {}).get("repair_priority") == "high":
                    response_parts.append("🔍 画像から重要な修理部品が検出されました。")
            
            # 音声分析結果の統合
            if analysis_results.get("audio_analysis"):
                audio_analysis = analysis_results["audio_analysis"]
                if audio_analysis.get("transcription"):
                    response_parts.append(f"🎤 音声内容: {audio_analysis['transcription']}")
            
            return "\n".join(response_parts) if response_parts else "分析結果を統合中です..."
            
        except Exception as e:
            return f"統合レスポンス生成エラー: {e}"

# === 使用例 ===
if __name__ == "__main__":
    # 高度機能のテスト
    async def test_advanced_features():
        advanced = AdvancedFeatures()
        
        # マルチモーダル入力のテスト
        test_input = {
            "text": "バッテリーが上がりません",
            "image": None,  # 実際の使用時はBase64エンコードされた画像
            "audio": None   # 実際の使用時は音声データ
        }
        
        result = await advanced.process_multimodal_input(test_input)
        print("高度機能テスト結果:", json.dumps(result, ensure_ascii=False, indent=2))
    
    # テスト実行
    asyncio.run(test_advanced_features())
