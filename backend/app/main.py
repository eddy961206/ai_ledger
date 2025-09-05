from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
# from app.services.scheduler_service import scheduler_service  # 임시 비활성화

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
try:
    from app.api.auth import router as auth_router
    app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
except ImportError:
    pass

try:
    from app.api.users import router as users_router
    app.include_router(users_router, prefix="/api/users", tags=["users"])
except ImportError:
    pass

try:
    from app.api.transactions import router as transactions_router
    app.include_router(transactions_router, prefix="/api/transactions", tags=["transactions"])
except ImportError:
    pass

try:
    from app.api.merchants import router as merchants_router
    app.include_router(merchants_router, prefix="/api/merchants", tags=["merchants"])
except ImportError:
    pass

try:
    from app.api.external_apis import router as external_apis_router
    app.include_router(external_apis_router, prefix="/api/external", tags=["external-apis"])
except ImportError:
    pass

try:
    from app.api.ai_engine import router as ai_engine_router
    app.include_router(ai_engine_router, prefix="/api/ai", tags=["ai-engine"])
except ImportError:
    pass

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    # 스케줄러 시작 (임시 비활성화)
    # scheduler_service.start()
    pass

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    # 스케줄러 중지 (임시 비활성화)
    # scheduler_service.stop()
    pass

@app.get("/")
def read_root():
    return {"message": "AI Household Ledger API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

