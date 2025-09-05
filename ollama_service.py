import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from ..core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

class OllamaService:
    """Ollama 로컬 LLM 연동 서비스"""
    
    def __init__(self, server_url: str = None):
        self.server_url = server_url or settings.default_ollama_server_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def is_available(self) -> bool:
        """Ollama 서버 연결 가능 여부 확인"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(f"{self.server_url}/api/tags", timeout=5) as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"Ollama 서버 연결 실패: {e}")
            return False
    
    async def get_available_models(self) -> List[str]:
        """사용 가능한 모델 목록 조회"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(f"{self.server_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return [model["name"] for model in data.get("models", [])]
                return []
        except Exception as e:
            logger.error(f"Ollama 모델 목록 조회 실패: {e}")
            return []
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response(
        self, 
        prompt: str, 
        model: str = "llama3", 
        system_prompt: str = None
    ) -> Dict[str, Any]:
        """Ollama를 통한 텍스트 생성"""
        if not self.session:
            raise RuntimeError("Service not initialized. Use async context manager.")
        
        try:
            # 요청 데이터 구성
            request_data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                request_data["system"] = system_prompt
            
            async with self.session.post(
                f"{self.server_url}/api/generate",
                json=request_data,
                timeout=60
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "response": result.get("response", ""),
                        "model": model,
                        "total_duration": result.get("total_duration", 0),
                        "load_duration": result.get("load_duration", 0),
                        "prompt_eval_count": result.get("prompt_eval_count", 0),
                        "eval_count": result.get("eval_count", 0)
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "요청 시간 초과"
            }
        except Exception as e:
            logger.error(f"Ollama 응답 생성 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_spending_patterns(
        self, 
        transactions: List[Dict[str, Any]], 
        model: str = "llama3"
    ) -> Dict[str, Any]:
        """Ollama를 통한 소비 패턴 분석"""
        try:
            # 거래 데이터 요약
            transaction_summary = self._prepare_transaction_summary(transactions)
            
            # 분석 프롬프트 생성
            system_prompt = """당신은 개인 금융 분석 전문가입니다. 사용자의 거래 데이터를 분석하여 소비 패턴을 파악하고 유용한 인사이트를 제공해주세요. 응답은 반드시 JSON 형식으로 제공해야 합니다."""
            
            prompt = self._create_analysis_prompt(transaction_summary)
            
            # Ollama API 호출
            result = await self.generate_response(prompt, model, system_prompt)
            
            if result["success"]:
                # JSON 응답 파싱
                analysis_result = self._parse_json_response(result["response"])
                analysis_result["model_used"] = model
                analysis_result["processing_time"] = result.get("total_duration", 0)
                return analysis_result
            else:
                return {"error": result["error"]}
                
        except Exception as e:
            logger.error(f"Ollama 소비 패턴 분석 실패: {e}")
            return {"error": str(e)}
    
    async def generate_monthly_report(
        self, 
        transactions: List[Dict[str, Any]], 
        previous_month_data: Dict[str, Any] = None,
        model: str = "llama3"
    ) -> Dict[str, Any]:
        """Ollama를 통한 월간 리포트 생성"""
        try:
            # 월간 데이터 요약
            monthly_summary = self._prepare_monthly_summary(transactions, previous_month_data)
            
            # 리포트 생성 프롬프트
            system_prompt = """당신은 개인 금융 리포트 작성 전문가입니다. 월간 소비 데이터를 바탕으로 상세하고 유용한 리포트를 작성해주세요. 응답은 반드시 JSON 형식으로 제공해야 합니다."""
            
            prompt = self._create_report_prompt(monthly_summary)
            
            # Ollama API 호출
            result = await self.generate_response(prompt, model, system_prompt)
            
            if result["success"]:
                # JSON 응답 파싱
                report_result = self._parse_json_response(result["response"])
                report_result["model_used"] = model
                report_result["processing_time"] = result.get("total_duration", 0)
                return report_result
            else:
                return {"error": result["error"]}
                
        except Exception as e:
            logger.error(f"Ollama 월간 리포트 생성 실패: {e}")
            return {"error": str(e)}
    
    def _prepare_transaction_summary(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """거래 데이터 요약 준비 (Gemini 서비스와 동일)"""
        if not transactions:
            return {"total_transactions": 0, "categories": {}, "total_amount": 0}
        
        categories = {}
        total_amount = 0
        
        for transaction in transactions:
            amount = float(transaction.get("amount", 0))
            category = transaction.get("manual_category", "기타")
            
            if category not in categories:
                categories[category] = {"count": 0, "amount": 0}
            
            categories[category]["count"] += 1
            categories[category]["amount"] += amount
            total_amount += amount
        
        return {
            "total_transactions": len(transactions),
            "total_amount": total_amount,
            "categories": categories
        }
    
    def _prepare_monthly_summary(
        self, 
        transactions: List[Dict[str, Any]], 
        previous_month_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """월간 요약 데이터 준비"""
        current_summary = self._prepare_transaction_summary(transactions)
        
        return {
            "current_month": current_summary,
            "previous_month": previous_month_data or {},
            "comparison_available": bool(previous_month_data)
        }
    
    def _create_analysis_prompt(self, transaction_summary: Dict[str, Any]) -> str:
        """소비 패턴 분석 프롬프트 생성"""
        prompt = f"""
다음 거래 데이터를 분석하여 사용자의 소비 패턴을 분석해주세요.

거래 요약:
- 총 거래 건수: {transaction_summary['total_transactions']}건
- 총 소비 금액: {transaction_summary['total_amount']:,.0f}원

카테고리별 소비:
"""
        
        for category, data in transaction_summary['categories'].items():
            prompt += f"- {category}: {data['amount']:,.0f}원 ({data['count']}건)\n"
        
        prompt += """

다음 형식의 JSON으로 분석 결과를 제공해주세요:
{
    "summary": "전체 소비 패턴 요약 (한글)",
    "category_analysis": {
        "카테고리명": {
            "percentage": 전체_대비_비율,
            "insight": "해당_카테고리_분석_내용"
        }
    },
    "spending_habits": ["주요_소비_습관_1", "주요_소비_습관_2"],
    "recommendations": ["개선_제안_1", "개선_제안_2"]
}

JSON 형식만 응답해주세요.
"""
        
        return prompt
    
    def _create_report_prompt(self, monthly_summary: Dict[str, Any]) -> str:
        """월간 리포트 생성 프롬프트"""
        current = monthly_summary['current_month']
        
        prompt = f"""
다음 월간 소비 데이터를 바탕으로 상세한 월간 리포트를 작성해주세요.

이번 달 소비 현황:
- 총 소비 금액: {current['total_amount']:,.0f}원
- 총 거래 건수: {current['total_transactions']}건

카테고리별 소비:
"""
        
        for category, data in current['categories'].items():
            prompt += f"- {category}: {data['amount']:,.0f}원 ({data['count']}건)\n"
        
        prompt += """

다음 형식의 JSON으로 월간 리포트를 제공해주세요:
{
    "title": "YYYY년_MM월_소비_리포트",
    "executive_summary": "이번_달_소비_요약",
    "key_metrics": {
        "total_spending": 총소비금액,
        "transaction_count": 거래건수,
        "most_spent_category": "최대소비카테고리"
    },
    "category_breakdown": {
        "카테고리명": {
            "amount": 금액,
            "percentage": 비율,
            "analysis": "카테고리_분석"
        }
    },
    "insights": ["주요_인사이트_1", "주요_인사이트_2"],
    "next_month_goals": ["다음_달_목표_1", "다음_달_목표_2"]
}

JSON 형식만 응답해주세요.
"""
        
        return prompt
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """JSON 응답 파싱"""
        try:
            # JSON 부분 추출
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {"error": "JSON 형식을 찾을 수 없습니다", "raw_response": response_text}
        except json.JSONDecodeError as e:
            return {"error": f"JSON 파싱 실패: {str(e)}", "raw_response": response_text}

# 팩토리 함수
def create_ollama_service(server_url: str = None) -> OllamaService:
    """Ollama 서비스 인스턴스 생성"""
    return OllamaService(server_url)

