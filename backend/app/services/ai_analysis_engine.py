from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.user import User
from ..crud import transaction, ai_analysis_log
from .gemini_service import gemini_service
from .ollama_service import create_ollama_service
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

class AIAnalysisEngine:
    """AI 분석 엔진 통합 서비스 - Gemini/Ollama 하이브리드"""
    
    def __init__(self):
        self.cache = {}  # 간단한 메모리 캐시 (실제 운영에서는 Redis 등 사용)
        self.cache_ttl = 3600  # 1시간 캐시
    
    async def analyze_with_preferred_ai(
        self,
        user: User,
        transactions_data: List[Dict[str, Any]],
        analysis_type: str = "pattern",
        db: Session = None
    ) -> Dict[str, Any]:
        """사용자 선호 AI 모델로 분석 수행 (하이브리드 로직)"""
        
        # 캐시 확인
        cache_key = self._generate_cache_key(user.id, transactions_data, analysis_type)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            logger.info(f"캐시에서 분석 결과 반환: {cache_key}")
            return cached_result
        
        preferred_model = user.preferred_ai_model or "gemini"
        analysis_result = None
        model_used = preferred_model
        
        try:
            if preferred_model == "ollama":
                # Ollama 우선 시도
                analysis_result = await self._analyze_with_ollama(
                    user, transactions_data, analysis_type
                )
                
                # Ollama 실패 시 Gemini로 fallback
                if not analysis_result or "error" in analysis_result:
                    logger.warning("Ollama 분석 실패, Gemini로 fallback")
                    analysis_result = await self._analyze_with_gemini(
                        transactions_data, analysis_type
                    )
                    model_used = "gemini"
            
            elif preferred_model == "hybrid":
                # 하이브리드 모드: 두 모델 모두 사용하여 결과 비교
                analysis_result = await self._analyze_with_hybrid(
                    user, transactions_data, analysis_type
                )
                model_used = "hybrid"
            
            else:
                # Gemini 기본 사용
                analysis_result = await self._analyze_with_gemini(
                    transactions_data, analysis_type
                )
                model_used = "gemini"
            
            # 결과 캐싱
            if analysis_result and "error" not in analysis_result:
                self._save_to_cache(cache_key, analysis_result)
            
            # 분석 로그 저장
            if db:
                ai_analysis_log.create_log(
                    db,
                    user_id=user.id,
                    request_payload={
                        "analysis_type": analysis_type,
                        "transaction_count": len(transactions_data),
                        "preferred_model": preferred_model
                    },
                    response_payload=analysis_result or {},
                    ai_model_used=model_used,
                    status="success" if analysis_result and "error" not in analysis_result else "error",
                    error_message=analysis_result.get("error") if analysis_result else None
                )
            
            return {
                "model_used": model_used,
                "analysis": analysis_result,
                "cached": False
            }
            
        except Exception as e:
            logger.error(f"AI 분석 엔진 오류: {e}")
            
            # 에러 로그 저장
            if db:
                ai_analysis_log.create_log(
                    db,
                    user_id=user.id,
                    request_payload={
                        "analysis_type": analysis_type,
                        "transaction_count": len(transactions_data)
                    },
                    response_payload={},
                    ai_model_used=preferred_model,
                    status="error",
                    error_message=str(e)
                )
            
            return {
                "model_used": preferred_model,
                "analysis": {"error": str(e)},
                "cached": False
            }
    
    async def _analyze_with_gemini(
        self, 
        transactions_data: List[Dict[str, Any]], 
        analysis_type: str
    ) -> Dict[str, Any]:
        """Gemini를 사용한 분석"""
        try:
            if analysis_type == "pattern":
                return await gemini_service.analyze_spending_patterns(transactions_data)
            elif analysis_type == "report":
                return await gemini_service.generate_monthly_report(transactions_data)
            elif analysis_type == "optimization":
                return await gemini_service.suggest_budget_optimization(transactions_data)
            else:
                return {"error": f"지원하지 않는 분석 타입: {analysis_type}"}
        except Exception as e:
            logger.error(f"Gemini 분석 실패: {e}")
            return {"error": str(e)}
    
    async def _analyze_with_ollama(
        self, 
        user: User, 
        transactions_data: List[Dict[str, Any]], 
        analysis_type: str
    ) -> Dict[str, Any]:
        """Ollama를 사용한 분석"""
        try:
            ollama_service = create_ollama_service(user.ollama_server_url)
            
            async with ollama_service as ollama:
                # Ollama 서버 연결 확인
                if not await ollama.is_available():
                    return {"error": "Ollama 서버에 연결할 수 없습니다"}
                
                # 사용 가능한 모델 확인
                available_models = await ollama.get_available_models()
                if not available_models:
                    return {"error": "사용 가능한 Ollama 모델이 없습니다"}
                
                # 기본 모델 선택 (llama3 우선, 없으면 첫 번째 모델)
                model_to_use = "llama3" if "llama3" in available_models else available_models[0]
                
                if analysis_type == "pattern":
                    return await ollama.analyze_spending_patterns(transactions_data, model_to_use)
                elif analysis_type == "report":
                    return await ollama.generate_monthly_report(transactions_data, model=model_to_use)
                else:
                    return {"error": f"Ollama에서 지원하지 않는 분석 타입: {analysis_type}"}
                    
        except Exception as e:
            logger.error(f"Ollama 분석 실패: {e}")
            return {"error": str(e)}
    
    async def _analyze_with_hybrid(
        self, 
        user: User, 
        transactions_data: List[Dict[str, Any]], 
        analysis_type: str
    ) -> Dict[str, Any]:
        """하이브리드 모드: Gemini와 Ollama 결과 비교"""
        try:
            # 두 모델로 동시 분석
            gemini_task = self._analyze_with_gemini(transactions_data, analysis_type)
            ollama_task = self._analyze_with_ollama(user, transactions_data, analysis_type)
            
            gemini_result, ollama_result = await asyncio.gather(
                gemini_task, ollama_task, return_exceptions=True
            )
            
            # 결과 통합
            hybrid_result = {
                "analysis_type": analysis_type,
                "gemini_result": gemini_result if not isinstance(gemini_result, Exception) else {"error": str(gemini_result)},
                "ollama_result": ollama_result if not isinstance(ollama_result, Exception) else {"error": str(ollama_result)},
                "comparison": self._compare_results(gemini_result, ollama_result),
                "recommended_result": self._select_best_result(gemini_result, ollama_result)
            }
            
            return hybrid_result
            
        except Exception as e:
            logger.error(f"하이브리드 분석 실패: {e}")
            return {"error": str(e)}
    
    def _compare_results(
        self, 
        gemini_result: Dict[str, Any], 
        ollama_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """두 AI 모델 결과 비교"""
        comparison = {
            "gemini_success": "error" not in gemini_result if isinstance(gemini_result, dict) else False,
            "ollama_success": "error" not in ollama_result if isinstance(ollama_result, dict) else False,
            "consistency_score": 0.0,
            "differences": []
        }
        
        # 두 결과가 모두 성공한 경우 일관성 점수 계산
        if comparison["gemini_success"] and comparison["ollama_success"]:
            # 간단한 일관성 점수 계산 (실제로는 더 정교한 비교 로직 필요)
            gemini_summary = gemini_result.get("summary", "")
            ollama_summary = ollama_result.get("summary", "")
            
            # 키워드 기반 유사도 계산 (간단한 예시)
            if gemini_summary and ollama_summary:
                common_words = set(gemini_summary.split()) & set(ollama_summary.split())
                total_words = set(gemini_summary.split()) | set(ollama_summary.split())
                comparison["consistency_score"] = len(common_words) / len(total_words) if total_words else 0
        
        return comparison
    
    def _select_best_result(
        self, 
        gemini_result: Dict[str, Any], 
        ollama_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """최적의 결과 선택"""
        # Gemini 결과가 성공하고 Ollama가 실패한 경우
        if isinstance(gemini_result, dict) and "error" not in gemini_result:
            if isinstance(ollama_result, dict) and "error" in ollama_result:
                return {"source": "gemini", "result": gemini_result}
        
        # Ollama 결과가 성공하고 Gemini가 실패한 경우
        if isinstance(ollama_result, dict) and "error" not in ollama_result:
            if isinstance(gemini_result, dict) and "error" in gemini_result:
                return {"source": "ollama", "result": ollama_result}
        
        # 둘 다 성공한 경우 Gemini 우선 (더 안정적)
        if (isinstance(gemini_result, dict) and "error" not in gemini_result and
            isinstance(ollama_result, dict) and "error" not in ollama_result):
            return {"source": "gemini", "result": gemini_result}
        
        # 둘 다 실패한 경우
        return {"source": "none", "result": {"error": "모든 AI 모델 분석 실패"}}
    
    def _generate_cache_key(
        self, 
        user_id: str, 
        transactions_data: List[Dict[str, Any]], 
        analysis_type: str
    ) -> str:
        """캐시 키 생성"""
        # 거래 데이터의 해시값을 사용하여 캐시 키 생성
        transactions_hash = hash(json.dumps(transactions_data, sort_keys=True, default=str))
        return f"ai_analysis:{user_id}:{analysis_type}:{transactions_hash}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """캐시에서 결과 조회"""
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            # TTL 확인
            if datetime.now().timestamp() - cached_data["timestamp"] < self.cache_ttl:
                return cached_data["data"]
            else:
                # 만료된 캐시 삭제
                del self.cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """캐시에 결과 저장"""
        self.cache[cache_key] = {
            "data": data,
            "timestamp": datetime.now().timestamp()
        }
        
        # 캐시 크기 제한 (간단한 LRU)
        if len(self.cache) > 100:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
    
    def clear_cache(self, user_id: str = None) -> None:
        """캐시 삭제"""
        if user_id:
            # 특정 사용자 캐시만 삭제
            keys_to_delete = [k for k in self.cache.keys() if k.startswith(f"ai_analysis:{user_id}:")]
            for key in keys_to_delete:
                del self.cache[key]
        else:
            # 전체 캐시 삭제
            self.cache.clear()
    
    async def get_analysis_performance_metrics(self, user_id: str, db: Session) -> Dict[str, Any]:
        """AI 분석 성능 메트릭 조회"""
        try:
            # 최근 30일간의 분석 로그 조회
            logs = ai_analysis_log.get_by_user(db, user_id=user_id, limit=100)
            
            if not logs:
                return {"message": "분석 로그가 없습니다"}
            
            # 성능 메트릭 계산
            total_analyses = len(logs)
            successful_analyses = len([log for log in logs if log.status == "success"])
            failed_analyses = total_analyses - successful_analyses
            
            model_usage = {}
            for log in logs:
                model = log.ai_model_used
                if model not in model_usage:
                    model_usage[model] = {"count": 0, "success": 0, "error": 0}
                model_usage[model]["count"] += 1
                if log.status == "success":
                    model_usage[model]["success"] += 1
                else:
                    model_usage[model]["error"] += 1
            
            return {
                "total_analyses": total_analyses,
                "success_rate": successful_analyses / total_analyses if total_analyses > 0 else 0,
                "successful_analyses": successful_analyses,
                "failed_analyses": failed_analyses,
                "model_usage": model_usage,
                "cache_size": len(self.cache)
            }
            
        except Exception as e:
            logger.error(f"성능 메트릭 조회 실패: {e}")
            return {"error": str(e)}

# 싱글톤 인스턴스
ai_analysis_engine = AIAnalysisEngine()

