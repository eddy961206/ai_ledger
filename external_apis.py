from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..core.database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..crud import transaction, merchant, ai_analysis_log
from ..services import woori_bank_service, google_places_service, gemini_service, create_ollama_service
from ..schemas.transaction import TransactionCreate

router = APIRouter()

@router.post("/sync-transactions")
async def sync_transactions(
    days_back: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """우리은행에서 거래 내역 동기화"""
    try:
        # 우리은행 API에서 거래 내역 조회
        async with woori_bank_service as bank_service:
            transactions_data = await bank_service.sync_user_transactions(
                str(current_user.id), days_back
            )
        
        if not transactions_data:
            return {"message": "동기화할 거래 내역이 없습니다.", "synced_count": 0}
        
        synced_count = 0
        
        for transaction_data in transactions_data:
            # 가맹점 정보 보강
            merchant_info = google_places_service.enrich_merchant_info(
                transaction_data["original_merchant_name"]
            )
            
            # 가맹점 생성 또는 조회
            existing_merchant = merchant.get_by_name(db, name=merchant_info["name"])
            if not existing_merchant:
                merchant_obj = merchant.create(db, obj_in=merchant_info)
            else:
                merchant_obj = existing_merchant
            
            # 거래 내역 생성
            transaction_create = TransactionCreate(
                merchant_id=merchant_obj.id,
                amount=transaction_data["amount"],
                transaction_type=transaction_data["transaction_type"],
                transaction_date=transaction_data["transaction_date"],
                original_merchant_name=transaction_data["original_merchant_name"],
                memo=transaction_data.get("memo", "")
            )
            
            transaction.create_with_user(db, obj_in=transaction_create, user_id=current_user.id)
            synced_count += 1
        
        return {
            "message": f"{synced_count}건의 거래 내역이 동기화되었습니다.",
            "synced_count": synced_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"거래 내역 동기화 실패: {str(e)}")

@router.post("/enrich-merchant/{merchant_id}")
async def enrich_merchant_info(
    merchant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """가맹점 정보 보강"""
    try:
        # 가맹점 조회
        merchant_obj = merchant.get(db, id=merchant_id)
        if not merchant_obj:
            raise HTTPException(status_code=404, detail="가맹점을 찾을 수 없습니다.")
        
        # Google Places로 정보 보강
        enriched_info = google_places_service.enrich_merchant_info(merchant_obj.name)
        
        # 가맹점 정보 업데이트
        updated_merchant = merchant.update(db, db_obj=merchant_obj, obj_in=enriched_info)
        
        return {
            "message": "가맹점 정보가 보강되었습니다.",
            "merchant": {
                "id": str(updated_merchant.id),
                "name": updated_merchant.name,
                "address": updated_merchant.address,
                "category": updated_merchant.category,
                "manual_category": updated_merchant.manual_category
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"가맹점 정보 보강 실패: {str(e)}")

@router.post("/ai-analysis")
async def analyze_spending_patterns(
    analysis_type: str = "pattern",  # pattern, report, optimization
    days_back: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """AI 소비 패턴 분석"""
    try:
        # 사용자 거래 내역 조회
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        user_transactions = transaction.get_by_user(db, user_id=current_user.id, limit=1000)
        
        # 기간 필터링
        filtered_transactions = [
            t for t in user_transactions 
            if start_date <= t.transaction_date <= end_date
        ]
        
        if not filtered_transactions:
            return {"message": "분석할 거래 내역이 없습니다.", "analysis": None}
        
        # 거래 데이터 변환
        transactions_data = []
        for t in filtered_transactions:
            transactions_data.append({
                "amount": float(t.amount),
                "transaction_type": t.transaction_type,
                "transaction_date": t.transaction_date,
                "original_merchant_name": t.original_merchant_name,
                "manual_category": getattr(t.merchant, 'manual_category', '기타') if t.merchant else '기타',
                "memo": t.memo
            })
        
        # AI 모델 선택 (사용자 설정에 따라)
        ai_model_used = current_user.preferred_ai_model or "gemini"
        analysis_result = None
        
        if ai_model_used == "gemini":
            # Gemini 분석
            if analysis_type == "pattern":
                analysis_result = await gemini_service.analyze_spending_patterns(transactions_data)
            elif analysis_type == "report":
                analysis_result = await gemini_service.generate_monthly_report(transactions_data)
            elif analysis_type == "optimization":
                analysis_result = await gemini_service.suggest_budget_optimization(transactions_data)
        
        elif ai_model_used == "ollama":
            # Ollama 분석
            ollama_service = create_ollama_service(current_user.ollama_server_url)
            async with ollama_service as ollama:
                if await ollama.is_available():
                    if analysis_type == "pattern":
                        analysis_result = await ollama.analyze_spending_patterns(transactions_data)
                    elif analysis_type == "report":
                        analysis_result = await ollama.generate_monthly_report(transactions_data)
                else:
                    # Ollama 연결 실패 시 Gemini로 fallback
                    if analysis_type == "pattern":
                        analysis_result = await gemini_service.analyze_spending_patterns(transactions_data)
                    elif analysis_type == "report":
                        analysis_result = await gemini_service.generate_monthly_report(transactions_data)
                    ai_model_used = "gemini"
        
        # 분석 로그 저장
        ai_analysis_log.create_log(
            db,
            user_id=current_user.id,
            request_payload={
                "analysis_type": analysis_type,
                "days_back": days_back,
                "transaction_count": len(transactions_data)
            },
            response_payload=analysis_result or {},
            ai_model_used=ai_model_used,
            status="success" if analysis_result and "error" not in analysis_result else "error",
            error_message=analysis_result.get("error") if analysis_result else "분석 결과 없음"
        )
        
        return {
            "analysis_type": analysis_type,
            "ai_model_used": ai_model_used,
            "transaction_count": len(transactions_data),
            "analysis": analysis_result
        }
        
    except Exception as e:
        # 에러 로그 저장
        ai_analysis_log.create_log(
            db,
            user_id=current_user.id,
            request_payload={"analysis_type": analysis_type, "days_back": days_back},
            response_payload={},
            ai_model_used=current_user.preferred_ai_model or "gemini",
            status="error",
            error_message=str(e)
        )
        
        raise HTTPException(status_code=500, detail=f"AI 분석 실패: {str(e)}")

@router.get("/ai-models")
async def get_available_ai_models(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """사용 가능한 AI 모델 목록 조회"""
    try:
        available_models = {
            "gemini": {
                "name": "Google Gemini",
                "available": bool(gemini_service.model),
                "description": "Google의 고성능 AI 모델"
            },
            "ollama": {
                "name": "Ollama (로컬)",
                "available": False,
                "models": [],
                "description": "로컬에서 실행되는 오픈소스 LLM"
            }
        }
        
        # Ollama 모델 확인
        if current_user.ollama_server_url:
            ollama_service = create_ollama_service(current_user.ollama_server_url)
            async with ollama_service as ollama:
                if await ollama.is_available():
                    available_models["ollama"]["available"] = True
                    available_models["ollama"]["models"] = await ollama.get_available_models()
        
        return {
            "current_preference": current_user.preferred_ai_model,
            "available_models": available_models
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 모델 조회 실패: {str(e)}")

@router.get("/analysis-logs")
async def get_analysis_logs(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """AI 분석 로그 조회"""
    try:
        logs = ai_analysis_log.get_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
        
        return [
            {
                "id": str(log.id),
                "request_timestamp": log.request_timestamp.isoformat(),
                "ai_model_used": log.ai_model_used,
                "status": log.status,
                "request_payload": log.request_payload,
                "response_payload": log.response_payload,
                "error_message": log.error_message
            }
            for log in logs
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 로그 조회 실패: {str(e)}")

