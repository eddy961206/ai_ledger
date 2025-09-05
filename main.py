from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import auth, users, transactions, merchants, external_apis, ai_engine
from .services.scheduler_service import scheduler_service

app = FastAPI(
    title="AI Household Ledger API",
    description="AI 인공지능 가계부 시스템 백엔드 API",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(merchants.router, prefix="/api/merchants", tags=["merchants"])
app.include_router(external_apis.router, prefix="/api/external", tags=["external-apis"])
app.include_router(ai_engine.router, prefix="/api/ai", tags=["ai-engine"])

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    # 스케줄러 시작
    scheduler_service.start()

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    # 스케줄러 중지
    scheduler_service.stop()

@app.get("/")
def read_root():
    return {"message": "AI Household Ledger API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

