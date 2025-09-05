# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running the Application
- **Start Backend**: `python run.py` (runs FastAPI on http://0.0.0.0:8000 with reload)
- **Alternative Start**: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

### Database Management
- **Database URL**: Configure in `.env` file (default: PostgreSQL on localhost:5432)
- **Migrations**: Uses Alembic for database migrations (`alembic.ini` configured)
- **Migration Scripts**: Located in `alembic/` directory (check if exists)

### Dependencies
- **Install**: `pip install -r requirements.txt`
- **Key Dependencies**: FastAPI, SQLAlchemy, PostgreSQL, Alembic, JWT auth, Google APIs

## System Architecture

This is an **AI-powered household ledger system** that integrates multiple external services:

### Core Components
- **Backend**: FastAPI application with modular architecture
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: React PWA (separate files in root: `*.jsx`, `*.js`, `*.css`)
- **Authentication**: JWT-based with user sessions

### External API Integrations
- **Woori Bank API**: Automated transaction collection (`woori_bank_service.py`)
- **Google Places API**: Merchant location/category enrichment (`google_places_service.py`)
- **AI Services**: Hybrid approach with Google Gemini and Ollama LLM
  - **Gemini Service**: `gemini_service.py` (cloud AI)
  - **Ollama Service**: `ollama_service.py` (local AI with fallback)
  - **AI Analysis Engine**: `ai_analysis_engine.py` (hybrid orchestration)

### Key Modules
- **User Management**: `users.py`, `user.py`, `auth.py`
- **Transaction Management**: `transactions.py`, `transaction.py`
- **Merchant Management**: `merchants.py`, `merchant.py`
- **AI Analysis**: `ai_engine.py`, `ai_analysis_engine.py`, `ai_analysis_log.py`
- **Scheduling**: `scheduler_service.py`, `scheduled_task.py` (automated tasks)
- **Configuration**: `config.py`, `env.py` (environment settings)
- **Security**: `security.py` (encryption, data protection)

### Data Flow Architecture
1. **Collection**: Bank API → Transaction data with merchant names
2. **Enrichment**: Google Places API → Enhanced merchant info (location, category)
3. **Analysis**: AI engines (Gemini/Ollama) → Spending pattern analysis
4. **Presentation**: React frontend → User dashboard and reports

## Environment Configuration

### Required Environment Variables (.env)
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key
- `WOORI_BANK_API_KEY`: Bank API access
- `GOOGLE_PLACES_API_KEY`: Places API access
- `GOOGLE_GEMINI_API_KEY`: Gemini AI access
- `DEFAULT_OLLAMA_SERVER_URL`: Local Ollama server (default: http://localhost:11434)

### AI Configuration
- System supports **hybrid AI mode**: Users can choose between Gemini (cloud) and Ollama (local)
- **Automatic fallback**: If Ollama fails, system falls back to Gemini
- AI settings are managed through React frontend settings page

## Database Schema
- **3-tier structure**: Users → Transactions → Merchants
- **Encryption**: Sensitive data (account numbers, transaction details) encrypted at rest
- **Compliance**: Designed for Korean personal data protection laws

## Security Features
- JWT authentication with configurable expiration
- Encrypted storage of sensitive financial data
- Environment variable management for API keys
- CORS middleware configured for cross-origin requests

## Development Notes
- **Language**: Korean documentation and comments throughout
- **Mixed Frontend**: React components (`.jsx`) and vanilla JS utilities coexist
- **Modular Design**: Each external service has dedicated module
- **Async Support**: FastAPI with async/await patterns
- **Logging**: AI requests/responses logged per user (`ai_analysis_log.py`)

## Project Structure
- **Flat Structure**: All Python modules in root directory
- **No Package Structure**: Import paths use relative imports from root
- **Mixed Assets**: HTML, CSS, JS, and JSX files alongside Python modules
- **Documentation**: Korean markdown files with architecture and deployment guides

- 응답은 모두 반말로 할 것
- 현재 환경 : 윈도우 11 상 WSL 에서 claude code 실행 중