import google.generativeai as genai
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from ..core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    """Google Gemini AI API 연동 서비스"""
    
    def __init__(self):
        self.api_key = settings.google_gemini_api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_spending_patterns(
        self, 
        transactions: List[Dict[str, Any]], 
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """소비 패턴 분석"""
        if not self.model:
            logger.warning("Gemini API 키가 설정되지 않았습니다.")
            return {"error": "Gemini API not configured"}
        
        try:
            # 거래 데이터 요약
            transaction_summary = self._prepare_transaction_summary(transactions)
            
            # 분석 프롬프트 생성
            prompt = self._create_analysis_prompt(transaction_summary, user_preferences)
            
            # Gemini API 호출
            response = self.model.generate_content(prompt)
            
            # 응답 파싱
            analysis_result = self._parse_analysis_response(response.text)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Gemini 소비 패턴 분석 실패: {e}")
            return {"error": str(e)}
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_monthly_report(
        self, 
        transactions: List[Dict[str, Any]], 
        previous_month_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """월간 소비 리포트 생성"""
        if not self.model:
            logger.warning("Gemini API 키가 설정되지 않았습니다.")
            return {"error": "Gemini API not configured"}
        
        try:
            # 월간 데이터 요약
            monthly_summary = self._prepare_monthly_summary(transactions, previous_month_data)
            
            # 리포트 생성 프롬프트
            prompt = self._create_report_prompt(monthly_summary)
            
            # Gemini API 호출
            response = self.model.generate_content(prompt)
            
            # 리포트 파싱
            report_result = self._parse_report_response(response.text)
            
            return report_result
            
        except Exception as e:
            logger.error(f"Gemini 월간 리포트 생성 실패: {e}")
            return {"error": str(e)}
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def suggest_budget_optimization(
        self, 
        transactions: List[Dict[str, Any]], 
        budget_goals: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """예산 최적화 제안"""
        if not self.model:
            logger.warning("Gemini API 키가 설정되지 않았습니다.")
            return {"error": "Gemini API not configured"}
        
        try:
            # 예산 분석 데이터 준비
            budget_analysis = self._prepare_budget_analysis(transactions, budget_goals)
            
            # 최적화 제안 프롬프트
            prompt = self._create_optimization_prompt(budget_analysis)
            
            # Gemini API 호출
            response = self.model.generate_content(prompt)
            
            # 제안 파싱
            optimization_result = self._parse_optimization_response(response.text)
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Gemini 예산 최적화 제안 실패: {e}")
            return {"error": str(e)}
    
    def _prepare_transaction_summary(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """거래 데이터 요약 준비"""
        if not transactions:
            return {"total_transactions": 0, "categories": {}, "total_amount": 0}
        
        categories = {}
        total_amount = 0
        
        for transaction in transactions:
            amount = float(transaction.get("amount", 0))
            category = transaction.get("manual_category", "기타")
            
            if category not in categories:
                categories[category] = {"count": 0, "amount": 0, "transactions": []}
            
            categories[category]["count"] += 1
            categories[category]["amount"] += amount
            categories[category]["transactions"].append({
                "merchant": transaction.get("original_merchant_name", ""),
                "amount": amount,
                "date": transaction.get("transaction_date", "").strftime("%Y-%m-%d") if transaction.get("transaction_date") else ""
            })
            
            total_amount += amount
        
        return {
            "total_transactions": len(transactions),
            "total_amount": total_amount,
            "categories": categories,
            "date_range": {
                "start": min(t.get("transaction_date", "") for t in transactions if t.get("transaction_date")),
                "end": max(t.get("transaction_date", "") for t in transactions if t.get("transaction_date"))
            }
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
    
    def _prepare_budget_analysis(
        self, 
        transactions: List[Dict[str, Any]], 
        budget_goals: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """예산 분석 데이터 준비"""
        summary = self._prepare_transaction_summary(transactions)
        
        budget_analysis = {
            "spending_by_category": summary["categories"],
            "total_spending": summary["total_amount"],
            "budget_goals": budget_goals or {},
            "overspent_categories": [],
            "underspent_categories": []
        }
        
        if budget_goals:
            for category, budget in budget_goals.items():
                actual_spending = summary["categories"].get(category, {}).get("amount", 0)
                if actual_spending > budget:
                    budget_analysis["overspent_categories"].append({
                        "category": category,
                        "budget": budget,
                        "actual": actual_spending,
                        "overspent": actual_spending - budget
                    })
                else:
                    budget_analysis["underspent_categories"].append({
                        "category": category,
                        "budget": budget,
                        "actual": actual_spending,
                        "remaining": budget - actual_spending
                    })
        
        return budget_analysis
    
    def _create_analysis_prompt(
        self, 
        transaction_summary: Dict[str, Any], 
        user_preferences: Dict[str, Any] = None
    ) -> str:
        """소비 패턴 분석 프롬프트 생성"""
        prompt = f"""
다음 거래 데이터를 분석하여 사용자의 소비 패턴을 분석해주세요.

거래 요약:
- 총 거래 건수: {transaction_summary['total_transactions']}건
- 총 소비 금액: {transaction_summary['total_amount']:,.0f}원
- 분석 기간: {transaction_summary.get('date_range', {}).get('start', '')} ~ {transaction_summary.get('date_range', {}).get('end', '')}

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
            "percentage": 전체 대비 비율,
            "trend": "증가/감소/유지",
            "insight": "해당 카테고리 분석 내용"
        }
    },
    "spending_habits": [
        "주요 소비 습관 1",
        "주요 소비 습관 2"
    ],
    "recommendations": [
        "개선 제안 1",
        "개선 제안 2"
    ],
    "risk_factors": [
        "주의할 점 1",
        "주의할 점 2"
    ]
}
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
        
        if monthly_summary['comparison_available']:
            previous = monthly_summary['previous_month']
            prompt += f"""

지난 달 대비 변화:
- 지난 달 총 소비: {previous.get('total_amount', 0):,.0f}원
- 증감: {current['total_amount'] - previous.get('total_amount', 0):,.0f}원
"""
        
        prompt += """

다음 형식의 JSON으로 월간 리포트를 제공해주세요:
{
    "title": "YYYY년 MM월 소비 리포트",
    "executive_summary": "이번 달 소비 요약 (한글)",
    "key_metrics": {
        "total_spending": 총소비금액,
        "transaction_count": 거래건수,
        "average_per_transaction": 건당평균금액,
        "most_spent_category": "최대소비카테고리",
        "most_frequent_category": "최다거래카테고리"
    },
    "category_breakdown": {
        "카테고리명": {
            "amount": 금액,
            "percentage": 비율,
            "transaction_count": 거래건수,
            "analysis": "카테고리 분석"
        }
    },
    "trends_and_insights": [
        "주요 트렌드 1",
        "주요 인사이트 2"
    ],
    "next_month_goals": [
        "다음 달 목표 1",
        "다음 달 목표 2"
    ],
    "action_items": [
        "실행 과제 1",
        "실행 과제 2"
    ]
}
"""
        
        return prompt
    
    def _create_optimization_prompt(self, budget_analysis: Dict[str, Any]) -> str:
        """예산 최적화 프롬프트 생성"""
        prompt = f"""
다음 예산 분석 데이터를 바탕으로 예산 최적화 제안을 해주세요.

현재 소비 현황:
- 총 소비: {budget_analysis['total_spending']:,.0f}원

카테고리별 소비:
"""
        
        for category, data in budget_analysis['spending_by_category'].items():
            prompt += f"- {category}: {data['amount']:,.0f}원\n"
        
        if budget_analysis['budget_goals']:
            prompt += "\n예산 목표 대비 현황:\n"
            for item in budget_analysis['overspent_categories']:
                prompt += f"- {item['category']}: 예산 {item['budget']:,.0f}원, 실제 {item['actual']:,.0f}원 (초과 {item['overspent']:,.0f}원)\n"
        
        prompt += """

다음 형식의 JSON으로 최적화 제안을 제공해주세요:
{
    "optimization_score": 1-100점,
    "priority_actions": [
        {
            "category": "카테고리명",
            "action": "구체적 행동",
            "expected_savings": 예상절약금액,
            "difficulty": "쉬움/보통/어려움"
        }
    ],
    "budget_recommendations": {
        "카테고리명": 권장예산금액
    },
    "saving_strategies": [
        "절약 전략 1",
        "절약 전략 2"
    ],
    "long_term_goals": [
        "장기 목표 1",
        "장기 목표 2"
    ]
}
"""
        
        return prompt
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """분석 응답 파싱"""
        try:
            # JSON 부분 추출
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {"error": "JSON 형식을 찾을 수 없습니다", "raw_response": response_text}
        except json.JSONDecodeError:
            return {"error": "JSON 파싱 실패", "raw_response": response_text}
    
    def _parse_report_response(self, response_text: str) -> Dict[str, Any]:
        """리포트 응답 파싱"""
        return self._parse_analysis_response(response_text)
    
    def _parse_optimization_response(self, response_text: str) -> Dict[str, Any]:
        """최적화 응답 파싱"""
        return self._parse_analysis_response(response_text)

# 싱글톤 인스턴스
gemini_service = GeminiService()

