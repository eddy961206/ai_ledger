# AI 인공지능 가계부 시스템 배포 가이드

**작성자**: Manus AI  
**작성일**: 2024년 9월 5일  
**버전**: 1.0.0

## 목차

1. [시스템 개요](#시스템-개요)
2. [배포 환경 요구사항](#배포-환경-요구사항)
3. [백엔드 배포](#백엔드-배포)
4. [프론트엔드 배포](#프론트엔드-배포)
5. [데이터베이스 설정](#데이터베이스-설정)
6. [환경 변수 설정](#환경-변수-설정)
7. [외부 API 설정](#외부-api-설정)
8. [보안 설정](#보안-설정)
9. [모니터링 및 로깅](#모니터링-및-로깅)
10. [트러블슈팅](#트러블슈팅)

---

## 시스템 개요

AI 인공지능 가계부 시스템은 우리은행 API, Google Places API, 그리고 AI(Gemini/Ollama) 하이브리드 엔진을 활용하여 사용자의 소비 패턴을 자동으로 분석하고 인사이트를 제공하는 웹 애플리케이션입니다.

### 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React PWA     │    │   FastAPI       │    │   PostgreSQL    │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   External APIs │
                    │ • 우리은행 API   │
                    │ • Google Places │
                    │ • Gemini AI     │
                    │ • Ollama        │
                    └─────────────────┘
```

### 주요 기능

- **자동 거래 내역 수집**: 우리은행 오픈뱅킹 API를 통한 실시간 거래 데이터 동기화
- **가맹점 정보 보강**: Google Places API를 활용한 상세 위치 및 카테고리 정보 자동 매칭
- **AI 소비 분석**: Gemini와 Ollama를 활용한 하이브리드 AI 분석 엔진
- **실시간 대시보드**: React PWA 기반의 반응형 웹 애플리케이션
- **자동 스케줄링**: 정기적인 데이터 동기화 및 분석 리포트 생성

---

## 배포 환경 요구사항

### 하드웨어 요구사항

| 구분 | 최소 사양 | 권장 사양 |
|------|-----------|-----------|
| CPU | 2 Core | 4 Core 이상 |
| RAM | 4GB | 8GB 이상 |
| Storage | 20GB | 50GB 이상 |
| Network | 100Mbps | 1Gbps |

### 소프트웨어 요구사항

| 구분 | 버전 | 필수 여부 |
|------|------|-----------|
| Ubuntu | 20.04 LTS 이상 | 필수 |
| Python | 3.11 이상 | 필수 |
| Node.js | 18.0 이상 | 필수 |
| PostgreSQL | 13 이상 | 필수 |
| Nginx | 1.18 이상 | 권장 |
| Docker | 20.10 이상 | 선택 |

### 네트워크 요구사항

- **인바운드 포트**: 80 (HTTP), 443 (HTTPS), 22 (SSH)
- **아웃바운드 포트**: 443 (HTTPS API 호출), 5432 (PostgreSQL)
- **도메인**: SSL 인증서 적용을 위한 도메인 필요

---

## 백엔드 배포

### 1. 시스템 패키지 설치

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y python3.11 python3.11-pip python3.11-venv
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx certbot python3-certbot-nginx
sudo apt install -y git curl wget unzip
```

### 2. Python 가상환경 설정

```bash
# 프로젝트 디렉토리 생성
sudo mkdir -p /opt/ai-household-ledger
sudo chown $USER:$USER /opt/ai-household-ledger
cd /opt/ai-household-ledger

# 가상환경 생성 및 활성화
python3.11 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 애플리케이션 코드 배포

```bash
# Git 저장소에서 코드 클론
git clone https://github.com/your-repo/ai-household-ledger-backend.git backend
cd backend

# 환경 변수 파일 생성
cp .env.example .env
nano .env  # 환경 변수 설정
```

### 4. 데이터베이스 마이그레이션

```bash
# Alembic 마이그레이션 실행
alembic upgrade head

# 초기 데이터 생성 (선택사항)
python scripts/init_data.py
```

### 5. Systemd 서비스 설정

```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/ai-household-ledger.service
```

```ini
[Unit]
Description=AI Household Ledger Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/ai-household-ledger/backend
Environment=PATH=/opt/ai-household-ledger/venv/bin
ExecStart=/opt/ai-household-ledger/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl enable ai-household-ledger
sudo systemctl start ai-household-ledger
sudo systemctl status ai-household-ledger
```

---

## 프론트엔드 배포

### 1. Node.js 설치

```bash
# NodeSource 저장소 추가
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# pnpm 설치
npm install -g pnpm
```

### 2. 프론트엔드 빌드

```bash
# 프론트엔드 코드 클론
cd /opt/ai-household-ledger
git clone https://github.com/your-repo/ai-household-ledger-frontend.git frontend
cd frontend

# 의존성 설치
pnpm install

# 환경 변수 설정
cp .env.example .env.production
nano .env.production
```

```env
VITE_API_BASE_URL=https://your-domain.com/api
VITE_APP_TITLE=AI 가계부
```

```bash
# 프로덕션 빌드
pnpm run build
```

### 3. Nginx 설정

```bash
# Nginx 설정 파일 생성
sudo nano /etc/nginx/sites-available/ai-household-ledger
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # 프론트엔드 정적 파일
    location / {
        root /opt/ai-household-ledger/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # PWA 캐싱 설정
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API 프록시
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 헬스 체크
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
```

```bash
# 사이트 활성화
sudo ln -s /etc/nginx/sites-available/ai-household-ledger /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. SSL 인증서 설정

```bash
# Let's Encrypt SSL 인증서 발급
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 자동 갱신 설정
sudo crontab -e
# 다음 라인 추가: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 데이터베이스 설정

### 1. PostgreSQL 설치 및 설정

```bash
# PostgreSQL 설치
sudo apt install -y postgresql postgresql-contrib

# PostgreSQL 서비스 시작
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. 데이터베이스 및 사용자 생성

```bash
# PostgreSQL 사용자로 전환
sudo -u postgres psql

-- 데이터베이스 생성
CREATE DATABASE ai_household_ledger;

-- 사용자 생성 및 권한 부여
CREATE USER ai_ledger_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE ai_household_ledger TO ai_ledger_user;

-- 연결 종료
\q
```

### 3. 데이터베이스 보안 설정

```bash
# PostgreSQL 설정 파일 편집
sudo nano /etc/postgresql/13/main/postgresql.conf
```

```conf
# 연결 설정
listen_addresses = 'localhost'
port = 5432

# 보안 설정
ssl = on
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/etc/ssl/private/ssl-cert-snakeoil.key'
```

```bash
# 클라이언트 인증 설정
sudo nano /etc/postgresql/13/main/pg_hba.conf
```

```conf
# 로컬 연결만 허용
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

```bash
# PostgreSQL 재시작
sudo systemctl restart postgresql
```

### 4. 백업 설정

```bash
# 백업 스크립트 생성
sudo nano /opt/ai-household-ledger/scripts/backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/ai-household-ledger/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="ai_household_ledger"

mkdir -p $BACKUP_DIR

pg_dump -h localhost -U ai_ledger_user -d $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# 7일 이상 된 백업 파일 삭제
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

```bash
# 실행 권한 부여
chmod +x /opt/ai-household-ledger/scripts/backup_db.sh

# 일일 백업 크론잡 설정
sudo crontab -e
# 다음 라인 추가: 0 2 * * * /opt/ai-household-ledger/scripts/backup_db.sh
```

---

## 환경 변수 설정

### 백엔드 환경 변수 (.env)

```env
# 데이터베이스 설정
DATABASE_URL=postgresql://ai_ledger_user:secure_password_here@localhost:5432/ai_household_ledger

# JWT 보안 설정
SECRET_KEY=your-super-secret-jwt-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 외부 API 키
WOORI_BANK_API_KEY=your_woori_bank_api_key
WOORI_BANK_API_SECRET=your_woori_bank_api_secret
GOOGLE_PLACES_API_KEY=your_google_places_api_key
GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key

# Ollama 설정
DEFAULT_OLLAMA_SERVER_URL=http://localhost:11434

# 로깅 설정
LOG_LEVEL=INFO
LOG_FILE=/var/log/ai-household-ledger/app.log

# CORS 설정 (프로덕션에서는 구체적인 도메인 지정)
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### 프론트엔드 환경 변수 (.env.production)

```env
# API 엔드포인트
VITE_API_BASE_URL=https://your-domain.com/api

# 애플리케이션 설정
VITE_APP_TITLE=AI 가계부
VITE_APP_DESCRIPTION=스마트한 소비 분석 서비스

# Google Maps (선택사항)
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# 분석 도구 (선택사항)
VITE_GA_TRACKING_ID=your_google_analytics_id
```

---

## 외부 API 설정

### 1. 우리은행 오픈뱅킹 API

우리은행 오픈뱅킹 API 사용을 위해서는 다음 단계를 거쳐야 합니다:

1. **개발자 등록**: 우리은행 오픈뱅킹 포털(https://openapi.wooribank.com)에서 개발자 등록
2. **앱 등록**: 애플리케이션 정보 등록 및 API 키 발급
3. **테스트 계정**: 샌드박스 환경에서 테스트용 계정 생성
4. **운영 승인**: 실제 서비스 운영을 위한 심사 및 승인 절차

```python
# 우리은행 API 설정 예시
WOORI_BANK_CONFIG = {
    "base_url": "https://openapi.wooribank.com",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "redirect_uri": "https://your-domain.com/auth/callback",
    "scope": "inquiry transfer"
}
```

### 2. Google Places API

Google Cloud Console에서 Places API를 활성화하고 API 키를 발급받아야 합니다:

1. **Google Cloud Console** 접속
2. **새 프로젝트 생성** 또는 기존 프로젝트 선택
3. **Places API 활성화**
4. **API 키 생성** 및 제한 설정
5. **결제 정보 등록** (무료 할당량 초과 시)

```javascript
// Google Places API 사용량 모니터링
const PLACES_API_LIMITS = {
  daily_requests: 100000,
  requests_per_minute: 1000,
  cost_per_1000_requests: 17  // USD
};
```

### 3. Google Gemini API

Google AI Studio에서 Gemini API 키를 발급받습니다:

1. **Google AI Studio** 접속 (https://makersuite.google.com)
2. **API 키 생성**
3. **사용량 제한 설정**
4. **안전 설정 구성**

```python
# Gemini API 설정
GEMINI_CONFIG = {
    "model": "gemini-pro",
    "temperature": 0.7,
    "max_tokens": 2048,
    "safety_settings": {
        "harassment": "BLOCK_MEDIUM_AND_ABOVE",
        "hate_speech": "BLOCK_MEDIUM_AND_ABOVE"
    }
}
```

### 4. Ollama 로컬 설정

로컬 AI 모델 실행을 위한 Ollama 설정:

```bash
# Ollama 설치
curl -fsSL https://ollama.ai/install.sh | sh

# 모델 다운로드
ollama pull llama2
ollama pull gemma

# 서비스 시작
sudo systemctl start ollama
sudo systemctl enable ollama
```

---

## 보안 설정

### 1. 방화벽 설정

```bash
# UFW 방화벽 활성화
sudo ufw enable

# 필요한 포트만 개방
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# 불필요한 포트 차단
sudo ufw deny 8000/tcp   # 백엔드 직접 접근 차단
sudo ufw deny 5432/tcp   # PostgreSQL 외부 접근 차단
```

### 2. SSL/TLS 설정

```nginx
# Nginx SSL 설정 강화
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL 인증서
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL 보안 설정
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 보안 헤더
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

### 3. 애플리케이션 보안

```python
# FastAPI 보안 설정
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["your-domain.com", "www.your-domain.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 4. 데이터베이스 보안

```sql
-- 데이터베이스 암호화 설정
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/etc/ssl/certs/server.crt';
ALTER SYSTEM SET ssl_key_file = '/etc/ssl/private/server.key';

-- 연결 제한
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
```

---

## 모니터링 및 로깅

### 1. 로그 설정

```python
# 로깅 설정 (logging_config.py)
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                '/var/log/ai-household-ledger/app.log',
                maxBytes=10485760,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
```

### 2. 시스템 모니터링

```bash
# 시스템 리소스 모니터링 스크립트
#!/bin/bash
# /opt/ai-household-ledger/scripts/monitor.sh

LOG_FILE="/var/log/ai-household-ledger/system.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# CPU 사용률
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')

# 메모리 사용률
MEM_USAGE=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')

# 디스크 사용률
DISK_USAGE=$(df -h / | awk 'NR==2{printf "%s", $5}')

# 로그 기록
echo "$DATE - CPU: ${CPU_USAGE}%, Memory: ${MEM_USAGE}%, Disk: ${DISK_USAGE}" >> $LOG_FILE

# 임계값 초과 시 알림
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo "High CPU usage: ${CPU_USAGE}%" | mail -s "System Alert" admin@your-domain.com
fi
```

### 3. 애플리케이션 모니터링

```python
# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    try:
        # 데이터베이스 연결 확인
        db_status = await check_database_connection()
        
        # 외부 API 상태 확인
        api_status = await check_external_apis()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "database": db_status,
            "external_apis": api_status,
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service unavailable")
```

### 4. 로그 분석 및 알림

```bash
# 로그 분석 스크립트
#!/bin/bash
# /opt/ai-household-ledger/scripts/log_analysis.sh

LOG_FILE="/var/log/ai-household-ledger/app.log"
ERROR_COUNT=$(grep -c "ERROR" $LOG_FILE)
WARNING_COUNT=$(grep -c "WARNING" $LOG_FILE)

if [ $ERROR_COUNT -gt 10 ]; then
    echo "High error count: $ERROR_COUNT errors found" | \
    mail -s "Application Alert" admin@your-domain.com
fi

# 로그 로테이션
logrotate /etc/logrotate.d/ai-household-ledger
```

---

## 트러블슈팅

### 일반적인 문제 및 해결방법

#### 1. 백엔드 서비스 시작 실패

**증상**: `systemctl start ai-household-ledger` 실패

**해결방법**:
```bash
# 로그 확인
sudo journalctl -u ai-household-ledger -f

# 일반적인 원인들:
# 1. 환경 변수 오류
sudo nano /opt/ai-household-ledger/backend/.env

# 2. 포트 충돌
sudo netstat -tlnp | grep :8000

# 3. 권한 문제
sudo chown -R ubuntu:ubuntu /opt/ai-household-ledger
```

#### 2. 데이터베이스 연결 오류

**증상**: `FATAL: password authentication failed`

**해결방법**:
```bash
# PostgreSQL 사용자 비밀번호 재설정
sudo -u postgres psql
ALTER USER ai_ledger_user PASSWORD 'new_password';

# 연결 테스트
psql -h localhost -U ai_ledger_user -d ai_household_ledger
```

#### 3. 외부 API 호출 실패

**증상**: API 키 인증 오류 또는 할당량 초과

**해결방법**:
```python
# API 키 확인
import os
print(f"Gemini API Key: {os.getenv('GOOGLE_GEMINI_API_KEY')[:10]}...")

# 사용량 모니터링
async def check_api_quota():
    # Google Cloud Console에서 API 사용량 확인
    # 필요시 결제 정보 업데이트
    pass
```

#### 4. 프론트엔드 빌드 오류

**증상**: `pnpm run build` 실패

**해결방법**:
```bash
# 의존성 재설치
rm -rf node_modules pnpm-lock.yaml
pnpm install

# 환경 변수 확인
cat .env.production

# 메모리 부족 시
export NODE_OPTIONS="--max-old-space-size=4096"
pnpm run build
```

#### 5. SSL 인증서 문제

**증상**: HTTPS 접속 불가 또는 인증서 만료

**해결방법**:
```bash
# 인증서 상태 확인
sudo certbot certificates

# 수동 갱신
sudo certbot renew --force-renewal

# Nginx 설정 테스트
sudo nginx -t
sudo systemctl reload nginx
```

### 성능 최적화

#### 1. 데이터베이스 최적화

```sql
-- 인덱스 생성
CREATE INDEX idx_transactions_user_date ON transactions(user_id, transaction_date);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_merchants_name ON merchants(name);

-- 쿼리 성능 분석
EXPLAIN ANALYZE SELECT * FROM transactions WHERE user_id = 1 ORDER BY transaction_date DESC LIMIT 10;
```

#### 2. 캐싱 설정

```python
# Redis 캐싱 (선택사항)
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

#### 3. CDN 설정

```nginx
# 정적 파일 캐싱
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary Accept-Encoding;
    
    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_types text/css application/javascript image/svg+xml;
}
```

### 백업 및 복구

#### 1. 전체 시스템 백업

```bash
#!/bin/bash
# /opt/ai-household-ledger/scripts/full_backup.sh

BACKUP_DIR="/opt/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 데이터베이스 백업
pg_dump -h localhost -U ai_ledger_user ai_household_ledger > $BACKUP_DIR/database.sql

# 애플리케이션 코드 백업
tar -czf $BACKUP_DIR/application.tar.gz /opt/ai-household-ledger

# 설정 파일 백업
cp /etc/nginx/sites-available/ai-household-ledger $BACKUP_DIR/
cp /etc/systemd/system/ai-household-ledger.service $BACKUP_DIR/

# 로그 파일 백업
tar -czf $BACKUP_DIR/logs.tar.gz /var/log/ai-household-ledger
```

#### 2. 시스템 복구

```bash
#!/bin/bash
# /opt/ai-household-ledger/scripts/restore.sh

BACKUP_DATE=$1
BACKUP_DIR="/opt/backups/$BACKUP_DATE"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

# 서비스 중지
sudo systemctl stop ai-household-ledger
sudo systemctl stop nginx

# 데이터베이스 복구
dropdb -h localhost -U ai_ledger_user ai_household_ledger
createdb -h localhost -U ai_ledger_user ai_household_ledger
psql -h localhost -U ai_ledger_user ai_household_ledger < $BACKUP_DIR/database.sql

# 애플리케이션 복구
tar -xzf $BACKUP_DIR/application.tar.gz -C /

# 서비스 재시작
sudo systemctl start ai-household-ledger
sudo systemctl start nginx
```

이 배포 가이드를 통해 AI 인공지능 가계부 시스템을 안전하고 효율적으로 운영 환경에 배포할 수 있습니다. 각 단계별로 신중하게 진행하고, 문제 발생 시 트러블슈팅 섹션을 참조하여 해결하시기 바랍니다.

