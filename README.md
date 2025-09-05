# AI 가계부 시스템

AI 인공지능 가계부 시스템 - 스마트한 소비 분석과 예산 관리

## 📁 프로젝트 구조

```
ai_ledger/
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── api/            # API 라우터들
│   │   ├── core/           # 핵심 설정 (config, database, security)
│   │   ├── crud/           # 데이터베이스 조작 로직
│   │   ├── models/         # SQLAlchemy 모델들
│   │   ├── schemas/        # Pydantic 스키마들
│   │   ├── services/       # 외부 API 서비스들
│   │   └── main.py         # FastAPI 애플리케이션
│   ├── requirements.txt    # Python 의존성
│   ├── alembic.ini        # DB 마이그레이션 설정
│   └── run.py             # 서버 실행 스크립트
├── frontend/               # React PWA 프론트엔드
│   ├── public/            # 정적 파일들
│   ├── src/
│   │   ├── pages/         # React 페이지 컴포넌트들
│   │   ├── components/    # 재사용 가능한 컴포넌트들
│   │   ├── services/      # API 클라이언트, 상태 관리
│   │   └── utils/         # 유틸리티 함수들
│   └── package.json       # 프론트엔드 설정
├── docs/                  # 프로젝트 문서
├── scripts/               # 유틸리티 스크립트들
├── ai_ledger_venv/       # Python 가상환경
├── .env                  # 환경변수 설정
└── .gitignore           # Git 제외 파일 목록
```

## 🚀 실행 방법

### 백엔드 (포트 8000)
```bash
cd backend
source ../ai_ledger_venv/bin/activate
python run.py
```

### 프론트엔드 (포트 3001)
```bash
cd frontend
npm run dev
```

## 📋 주요 기능

- **은행 API 연동**: 우리은행 API를 통한 자동 거래내역 수집
- **AI 분석**: Google Gemini + Ollama 하이브리드 AI 분석 엔진
- **상점 정보**: Google Places API를 통한 상점 카테고리 자동 분류
- **PWA**: 모바일 앱처럼 사용 가능한 프로그레시브 웹앱
- **보안**: JWT 인증 + 민감 데이터 암호화

## 🔧 설정

`.env` 파일에서 필요한 API 키들을 설정하세요:
- `WOORI_BANK_API_KEY`: 우리은행 API 키
- `GOOGLE_PLACES_API_KEY`: Google Places API 키  
- `GOOGLE_GEMINI_API_KEY`: Google Gemini API 키
- `DATABASE_URL`: PostgreSQL 연결 문자열

## 📚 더 많은 정보

자세한 문서는 `docs/` 폴더를 참조하세요.