# Live Interpreter Pro - Backend

FastAPI backend for real-time interpretation platform.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your API keys

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

## Project Structure

- `app/main.py` - FastAPI application entry point
- `app/api/` - REST API endpoints
- `app/websocket/` - WebSocket handlers for real-time streaming
- `app/services/` - Business logic (STT, translation, payment)
- `app/models/` - Database models
- `app/schemas/` - Pydantic schemas
- `app/core/` - Configuration, security, database setup

