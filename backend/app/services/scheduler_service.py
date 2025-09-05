from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..crud import scheduled_task, user, transaction
from ..services.ai_analysis_engine import ai_analysis_engine
from ..services.woori_bank_service import woori_bank_service
import asyncio
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    """자동 스케줄링 서비스"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def start(self):
        """스케줄러 시작"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("스케줄러가 시작되었습니다.")
            
            # 기본 스케줄 작업 등록
            self._register_default_jobs()
    
    def stop(self):
        """스케줄러 중지"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("스케줄러가 중지되었습니다.")
    
    def _register_default_jobs(self):
        """기본 스케줄 작업 등록"""
        # 매일 오전 9시에 활성 스케줄 작업 확인
        self.scheduler.add_job(
            self._check_scheduled_tasks,
            CronTrigger(hour=9, minute=0),
            id="check_scheduled_tasks",
            replace_existing=True
        )
        
        # 매시간 캐시 정리
        self.scheduler.add_job(
            self._cleanup_cache,
            IntervalTrigger(hours=1),
            id="cleanup_cache",
            replace_existing=True
        )
    
    async def _check_scheduled_tasks(self):
        """활성 스케줄 작업 확인 및 실행"""
        try:
            db = SessionLocal()
            try:
                # 활성 스케줄 작업 조회
                active_tasks = scheduled_task.get_active_tasks(db)
                
                for task in active_tasks:
                    # 실행 시간 확인
                    if self._should_run_task(task):
                        await self._execute_scheduled_task(task, db)
                        
                        # 다음 실행 시간 업데이트
                        self._update_next_run_time(task, db)
                        
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"스케줄 작업 확인 실패: {e}")
    
    def _should_run_task(self, task) -> bool:
        """작업 실행 여부 확인"""
        now = datetime.now()
        
        # 다음 실행 시간이 설정되어 있고 현재 시간이 지났는지 확인
        if task.next_run_at and now >= task.next_run_at:
            return True
        
        # 마지막 실행 시간이 없는 경우 (첫 실행)
        if not task.last_run_at:
            return True
        
        return False
    
    async def _execute_scheduled_task(self, task, db: Session):
        """스케줄 작업 실행"""
        try:
            logger.info(f"스케줄 작업 실행: {task.task_type} (사용자: {task.user_id})")
            
            # 사용자 조회
            task_user = user.get(db, id=task.user_id)
            if not task_user:
                logger.error(f"사용자를 찾을 수 없습니다: {task.user_id}")
                return
            
            if task.task_type == "transaction_sync":
                await self._sync_user_transactions(task_user, db)
            elif task.task_type == "ai_report_generation":
                await self._generate_ai_report(task_user, db)
            elif task.task_type == "monthly_analysis":
                await self._generate_monthly_analysis(task_user, db)
            
            # 마지막 실행 시간 업데이트
            task.last_run_at = datetime.now()
            db.commit()
            
        except Exception as e:
            logger.error(f"스케줄 작업 실행 실패: {e}")
    
    async def _sync_user_transactions(self, task_user, db: Session):
        """사용자 거래 내역 동기화"""
        try:
            async with woori_bank_service as bank_service:
                transactions_data = await bank_service.sync_user_transactions(
                    str(task_user.id), days_back=7  # 최근 7일
                )
            
            logger.info(f"사용자 {task_user.username}의 거래 내역 {len(transactions_data)}건 동기화 완료")
            
        except Exception as e:
            logger.error(f"거래 내역 동기화 실패: {e}")
    
    async def _generate_ai_report(self, task_user, db: Session):
        """AI 리포트 생성"""
        try:
            # 최근 30일 거래 내역 조회
            user_transactions = transaction.get_by_user(db, user_id=task_user.id, limit=1000)
            
            # 기간 필터링
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            filtered_transactions = [
                t for t in user_transactions 
                if start_date <= t.transaction_date <= end_date
            ]
            
            if not filtered_transactions:
                logger.info(f"사용자 {task_user.username}의 분석할 거래 내역이 없습니다.")
                return
            
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
            
            # AI 분석 실행
            analysis_result = await ai_analysis_engine.analyze_with_preferred_ai(
                task_user, transactions_data, "report", db
            )
            
            logger.info(f"사용자 {task_user.username}의 AI 리포트 생성 완료")
            
        except Exception as e:
            logger.error(f"AI 리포트 생성 실패: {e}")
    
    async def _generate_monthly_analysis(self, task_user, db: Session):
        """월간 분석 생성"""
        try:
            # 이번 달 거래 내역 조회
            now = datetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            user_transactions = transaction.get_by_user(db, user_id=task_user.id, limit=1000)
            
            # 이번 달 거래만 필터링
            monthly_transactions = [
                t for t in user_transactions 
                if t.transaction_date >= start_of_month
            ]
            
            if not monthly_transactions:
                logger.info(f"사용자 {task_user.username}의 이번 달 거래 내역이 없습니다.")
                return
            
            # 거래 데이터 변환
            transactions_data = []
            for t in monthly_transactions:
                transactions_data.append({
                    "amount": float(t.amount),
                    "transaction_type": t.transaction_type,
                    "transaction_date": t.transaction_date,
                    "original_merchant_name": t.original_merchant_name,
                    "manual_category": getattr(t.merchant, 'manual_category', '기타') if t.merchant else '기타',
                    "memo": t.memo
                })
            
            # AI 분석 실행
            analysis_result = await ai_analysis_engine.analyze_with_preferred_ai(
                task_user, transactions_data, "pattern", db
            )
            
            logger.info(f"사용자 {task_user.username}의 월간 분석 완료")
            
        except Exception as e:
            logger.error(f"월간 분석 실패: {e}")
    
    def _update_next_run_time(self, task, db: Session):
        """다음 실행 시간 업데이트"""
        try:
            now = datetime.now()
            
            if task.schedule_type == "daily":
                task.next_run_at = now + timedelta(days=1)
            elif task.schedule_type == "weekly":
                task.next_run_at = now + timedelta(weeks=1)
            elif task.schedule_type == "monthly":
                # 다음 달 같은 날
                if now.month == 12:
                    next_month = now.replace(year=now.year + 1, month=1)
                else:
                    next_month = now.replace(month=now.month + 1)
                task.next_run_at = next_month
            elif task.schedule_type == "cron" and task.cron_expression:
                # Cron 표현식 파싱 (간단한 구현)
                task.next_run_at = self._parse_cron_next_run(task.cron_expression, now)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"다음 실행 시간 업데이트 실패: {e}")
    
    def _parse_cron_next_run(self, cron_expression: str, current_time: datetime) -> datetime:
        """Cron 표현식에서 다음 실행 시간 계산 (간단한 구현)"""
        try:
            # 실제로는 croniter 라이브러리 사용 권장
            # 여기서는 간단한 예시만 구현
            
            # "0 9 * * *" (매일 오전 9시) 형태 가정
            parts = cron_expression.split()
            if len(parts) >= 2:
                minute = int(parts[0]) if parts[0] != "*" else current_time.minute
                hour = int(parts[1]) if parts[1] != "*" else current_time.hour
                
                next_run = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # 오늘 시간이 지났으면 내일로
                if next_run <= current_time:
                    next_run += timedelta(days=1)
                
                return next_run
            
            # 파싱 실패 시 24시간 후
            return current_time + timedelta(days=1)
            
        except Exception:
            # 파싱 실패 시 24시간 후
            return current_time + timedelta(days=1)
    
    async def _cleanup_cache(self):
        """캐시 정리"""
        try:
            ai_analysis_engine.clear_cache()
            logger.info("AI 분석 캐시 정리 완료")
        except Exception as e:
            logger.error(f"캐시 정리 실패: {e}")
    
    def add_user_schedule(
        self, 
        user_id: str, 
        task_type: str, 
        schedule_type: str, 
        cron_expression: str = None
    ) -> bool:
        """사용자 스케줄 추가"""
        try:
            db = SessionLocal()
            try:
                # 스케줄 작업 생성
                from ..schemas.scheduled_task import ScheduledTaskCreate
                
                task_create = ScheduledTaskCreate(
                    task_type=task_type,
                    schedule_type=schedule_type,
                    cron_expression=cron_expression,
                    is_active=True
                )
                
                new_task = scheduled_task.create_with_user(db, obj_in=task_create, user_id=user_id)
                
                # 첫 실행 시간 설정
                self._update_next_run_time(new_task, db)
                
                logger.info(f"사용자 {user_id}의 스케줄 작업 추가: {task_type}")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"스케줄 추가 실패: {e}")
            return False
    
    def remove_user_schedule(self, user_id: str, task_id: str) -> bool:
        """사용자 스케줄 제거"""
        try:
            db = SessionLocal()
            try:
                task = scheduled_task.get(db, id=task_id)
                if task and str(task.user_id) == user_id:
                    task.is_active = False
                    db.commit()
                    logger.info(f"사용자 {user_id}의 스케줄 작업 비활성화: {task_id}")
                    return True
                return False
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"스케줄 제거 실패: {e}")
            return False

# 싱글톤 인스턴스
scheduler_service = SchedulerService()

