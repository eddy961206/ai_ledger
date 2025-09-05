import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class WooriBankService:
    """우리은행 오픈뱅킹/카드 API 연동 서비스"""
    
    def __init__(self):
        self.api_key = settings.woori_bank_api_key
        self.base_url = "https://openapi.wooribank.com"  # 실제 우리은행 API URL로 변경 필요
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """API 요청 공통 메서드"""
        if not self.session:
            raise RuntimeError("Service not initialized. Use async context manager.")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, headers=headers, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"우리은행 API 요청 실패: {e}")
            raise
    
    async def get_account_list(self, user_id: str) -> List[Dict[str, Any]]:
        """사용자 계좌 목록 조회"""
        try:
            endpoint = f"/v1/accounts/{user_id}"
            response = await self._make_request("GET", endpoint)
            return response.get("accounts", [])
        except Exception as e:
            logger.error(f"계좌 목록 조회 실패: {e}")
            return []
    
    async def get_card_transactions(
        self, 
        card_number: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """체크카드 거래 내역 조회"""
        try:
            endpoint = f"/v1/cards/{card_number}/transactions"
            params = {
                "start_date": start_date.strftime("%Y%m%d"),
                "end_date": end_date.strftime("%Y%m%d")
            }
            
            response = await self._make_request("GET", endpoint, params=params)
            transactions = response.get("transactions", [])
            
            # 거래 내역 정규화
            normalized_transactions = []
            for transaction in transactions:
                normalized_transaction = {
                    "amount": float(transaction.get("amount", 0)),
                    "transaction_type": transaction.get("transaction_type", "결제"),
                    "transaction_date": self._parse_date(transaction.get("transaction_date")),
                    "original_merchant_name": transaction.get("merchant_name", ""),
                    "memo": transaction.get("memo", ""),
                    "merchant_address": transaction.get("merchant_address", ""),
                    "merchant_category": transaction.get("merchant_category", "")
                }
                normalized_transactions.append(normalized_transaction)
            
            return normalized_transactions
            
        except Exception as e:
            logger.error(f"카드 거래 내역 조회 실패: {e}")
            return []
    
    async def get_account_transactions(
        self, 
        account_number: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """계좌 거래 내역 조회 (현금 이체 등)"""
        try:
            endpoint = f"/v1/accounts/{account_number}/transactions"
            params = {
                "start_date": start_date.strftime("%Y%m%d"),
                "end_date": end_date.strftime("%Y%m%d")
            }
            
            response = await self._make_request("GET", endpoint, params=params)
            transactions = response.get("transactions", [])
            
            # 거래 내역 정규화
            normalized_transactions = []
            for transaction in transactions:
                normalized_transaction = {
                    "amount": float(transaction.get("amount", 0)),
                    "transaction_type": transaction.get("transaction_type", "이체"),
                    "transaction_date": self._parse_date(transaction.get("transaction_date")),
                    "original_merchant_name": transaction.get("counterpart_name", "현금이체"),
                    "memo": transaction.get("memo", ""),
                    "counterpart_account": transaction.get("counterpart_account", "")
                }
                normalized_transactions.append(normalized_transaction)
            
            return normalized_transactions
            
        except Exception as e:
            logger.error(f"계좌 거래 내역 조회 실패: {e}")
            return []
    
    def _parse_date(self, date_str: str) -> datetime:
        """날짜 문자열을 datetime 객체로 변환"""
        try:
            # 우리은행 API 날짜 형식에 맞게 조정 필요
            if len(date_str) == 8:  # YYYYMMDD
                return datetime.strptime(date_str, "%Y%m%d")
            elif len(date_str) == 14:  # YYYYMMDDHHMMSS
                return datetime.strptime(date_str, "%Y%m%d%H%M%S")
            else:
                return datetime.now()
        except ValueError:
            logger.warning(f"날짜 파싱 실패: {date_str}")
            return datetime.now()
    
    async def sync_user_transactions(self, user_id: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """사용자의 모든 거래 내역 동기화"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        all_transactions = []
        
        try:
            # 계좌 목록 조회
            accounts = await self.get_account_list(user_id)
            
            for account in accounts:
                account_number = account.get("account_number")
                account_type = account.get("account_type")
                
                if account_type == "card":
                    # 카드 거래 내역 조회
                    transactions = await self.get_card_transactions(
                        account_number, start_date, end_date
                    )
                else:
                    # 계좌 거래 내역 조회
                    transactions = await self.get_account_transactions(
                        account_number, start_date, end_date
                    )
                
                all_transactions.extend(transactions)
            
            logger.info(f"사용자 {user_id}의 거래 내역 {len(all_transactions)}건 동기화 완료")
            return all_transactions
            
        except Exception as e:
            logger.error(f"거래 내역 동기화 실패: {e}")
            return []

# 싱글톤 인스턴스
woori_bank_service = WooriBankService()

