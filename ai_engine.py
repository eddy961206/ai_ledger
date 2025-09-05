from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..core.database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..crud import transaction, scheduled_task
from ..services.ai_analysis_engine import ai_analysis_engine
from ..services.scheduler_service import scheduler_service
from ..schemas.scheduled_task import ScheduledTaskCreate, ScheduledTaskResponse

router = APIRouter()

@router.post("/analyze")
async def analyze_with_ai_engine(
    analysis_type: str = "pattern",  # pattern, report, optimization
    days_back: int = 30,
    force_refresh: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """AI 분석 엔진을 통한 통합 분석"""
    try:
        # 캐시 강제 새로고침
        if force_refresh:
            ai_analysis_engine.clear_cache(str(current_user.id))
        
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
            return {
                "message": "분석할 거래 내역이 없습니다.",
                "analysis": None,
                "transaction_count": 0
            }
        
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
        
        # AI 분석 엔진 실행
        result = await ai_analysis_engine.analyze_with_preferred_ai(
            current_user, transactions_data, analysis_type, db
        )
        
        return {
            "analysis_type": analysis_type,
            "transaction_count": len(transactions_data),
            "days_analyzed": days_back,
            "model_used": result["model_used"],
            "cached": result["cached"],
            "analysis": result["analysis"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 분석 실패: {str(e)}")

@router.get("/performance")
async def get_ai_performance_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """AI 분석 성능 메트릭 조회"""
    try:
        metrics = await ai_analysis_engine.get_analysis_performance_metrics(
            str(current_user.id), db
        )
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"성능 메트릭 조회 실패: {str(e)}")

@router.post("/clear-cache")
async def clear_ai_cache(
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """AI 분석 캐시 삭제"""
    try:
        ai_analysis_engine.clear_cache(str(current_user.id))
        return {"message": "캐시가 삭제되었습니다."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"캐시 삭제 실패: {str(e)}")

@router.post("/schedule")
async def create_analysis_schedule(
    task_type: str,  # transaction_sync, ai_report_generation, monthly_analysis
    schedule_type: str,  # daily, weekly, monthly, cron
    cron_expression: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """AI 분석 스케줄 생성"""
    try:
        # 유효한 작업 타입 확인
        valid_task_types = ["transaction_sync", "ai_report_generation", "monthly_analysis"]
        if task_type not in valid_task_types:
            raise HTTPException(
                status_code=400, 
                detail=f"유효하지 않은 작업 타입입니다. 사용 가능한 타입: {valid_task_types}"
            )
        
        # 유효한 스케줄 타입 확인
        valid_schedule_types = ["daily", "weekly", "monthly", "cron"]
        if schedule_type not in valid_schedule_types:
            raise HTTPException(
                status_code=400,
                detail=f"유효하지 않은 스케줄 타입입니다. 사용 가능한 타입: {valid_schedule_types}"
            )
        
        # Cron 스케줄인 경우 표현식 필수
        if schedule_type == "cron" and not cron_expression:
            raise HTTPException(
                status_code=400,
                detail="Cron 스케줄 타입에는 cron_expression이 필요합니다."
            )
        
        # 스케줄 작업 생성
        task_create = ScheduledTaskCreate(
            task_type=task_type,
            schedule_type=schedule_type,
            cron_expression=cron_expression,
            is_active=True
        )
        
        created_task = scheduled_task.create_with_user(
            db, obj_in=task_create, user_id=current_user.id
        )
        
        # 스케줄러에 등록
        success = scheduler_service.add_user_schedule(
            str(current_user.id), task_type, schedule_type, cron_expression
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="스케줄러 등록 실패")
        
        return {
            "message": "스케줄이 생성되었습니다.",
            "schedule_id": str(created_task.id),
            "task_type": task_type,
            "schedule_type": schedule_type,
            "cron_expression": cron_expression
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"스케줄 생성 실패: {str(e)}")

@router.get("/schedules")
async def get_user_schedules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[ScheduledTaskResponse]:
    """사용자 스케줄 목록 조회"""
    try:
        user_schedules = scheduled_task.get_by_user(db, user_id=current_user.id)
        return user_schedules
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"스케줄 조회 실패: {str(e)}")

@router.delete("/schedule/{schedule_id}")
async def delete_analysis_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """AI 분석 스케줄 삭제"""
    try:
        # 스케줄 조회 및 권한 확인
        task = scheduled_task.get(db, id=schedule_id)
        if not task:
            raise HTTPException(status_code=404, detail="스케줄을 찾을 수 없습니다.")
        
        if task.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        
        # 스케줄 비활성화
        task.is_active = False
        db.commit()
        
        # 스케줄러에서 제거
        scheduler_service.remove_user_schedule(str(current_user.id), schedule_id)
        
        return {"message": "스케줄이 삭제되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"스케줄 삭제 실패: {str(e)}")

@router.post("/test-analysis")
async def test_ai_analysis(
    model_type: str = "auto",  # auto, gemini, ollama, hybrid
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """AI 분석 테스트 (개발/디버깅 용도)"""
    try:
        # 테스트용 더미 거래 데이터
        test_transactions = [
            {
                "amount": 15000,
                "transaction_type": "결제",
                "transaction_date": datetime.now() - timedelta(days=1),
                "original_merchant_name": "스타벅스 강남점",
                "manual_category": "식비",
                "memo": ""
            },
            {
                "amount": 50000,
                "transaction_type": "결제",
                "transaction_date": datetime.now() - timedelta(days=2),
                "original_merchant_name": "이마트 트레이더스",
                "manual_category": "쇼핑",
                "memo": ""
            },
            {
                "amount": 8000,
                "transaction_type": "결제",
                "transaction_date": datetime.now() - timedelta(days=3),
                "original_merchant_name": "지하철 교통카드",
                "manual_category": "교통",
                "memo": ""
            }
        ]
        
        # 모델 타입에 따른 분석
        if model_type != "auto":
            # 임시로 사용자 선호 모델 변경
            original_preference = current_user.preferred_ai_model
            current_user.preferred_ai_model = model_type
        
        result = await ai_analysis_engine.analyze_with_preferred_ai(
            current_user, test_transactions, "pattern", db
        )
        
        # 원래 설정 복원
        if model_type != "auto":
            current_user.preferred_ai_model = original_preference
        
        return {
            "test_mode": True,
            "model_requested": model_type,
            "model_used": result["model_used"],
            "test_data_count": len(test_transactions),
            "analysis": result["analysis"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 분석 테스트 실패: {str(e)}")

