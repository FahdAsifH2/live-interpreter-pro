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

3. Create `.env` file from `.env.example` and fill in your API keys:
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

4. Set up PostgreSQL database:
```bash
createdb live_interpreter_pro
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## Project Structure

- `app/main.py` - FastAPI application entry point
- `app/api/` - REST API endpoints
- `app/websocket/` - WebSocket handlers for real-time streaming
- `app/services/` - Business logic (STT, translation, payment)
- `app/models/` - Database models
- `app/schemas/` - Pydantic schemas
- `app/core/` - Configuration, security, database setup

## Environment Variables

Required:
- `SECRET_KEY` - Secret key for JWT tokens
- `DATABASE_URL` - PostgreSQL connection string
- `DEEPGRAM_API_KEY` - Deepgram API key for speech-to-text
- `DEEPL_API_KEY` - DeepL API key for translation

Optional:
- `AZURE_TRANSLATOR_KEY` - Azure Translator key (fallback)
- `AZURE_TRANSLATOR_ENDPOINT` - Azure Translator endpoint
- `STRIPE_SECRET_KEY` - Stripe secret key for payments
