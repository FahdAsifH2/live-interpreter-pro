# Live Interpreter Pro

A professional real-time interpretation platform for interpreters, providing instant speech-to-text and translation capabilities.

## Project Structure

```
live-interpreter-pro/
├── backend/          # FastAPI backend
│   ├── app/         # Application code
│   ├── tests/       # Test files
│   └── scripts/     # Utility scripts
├── frontend/        # Flutter application (Web + Mobile)
│   ├── lib/         # Dart source code
│   ├── assets/      # Images, fonts, etc.
│   └── test/        # Test files
├── docs/            # Documentation
├── deployment/      # Docker, AWS configs
└── README.md        # This file
```

## Features

- **Real-Time Speech-to-Text** - Using Deepgram Nova-2 for ultra-low latency transcription
- **Real-Time Translation** - DeepL API with Microsoft Translator fallback
- **Multi-Language Support** - English ↔ Spanish, Portuguese, French, Haitian Creole, Arabic, Mandarin, Russian, and more
- **Web + Mobile** - Simultaneous development for all platforms using Flutter
- **Interpreter Tools** - Glossary builder, vocabulary notebook, session transcripts, quick notepad
- **Privacy & Security** - TLS 1.3 encryption, zero-retention audio, PIN lock, privacy wipe
- **Subscription System** - Stripe (web) + Apple IAP + Google IAP with 15-day trials

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Flutter (Web, iOS, Android)
- **STT Provider**: Deepgram Nova-2
- **Translation**: DeepL + Microsoft Translator (fallback)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Deployment**: AWS
- **Real-time**: WebSockets

## Getting Started

### Backend Setup
See [backend/README.md](backend/README.md)

### Frontend Setup
See [frontend/README.md](frontend/README.md)

## Project Timeline

- **Month 1**: MVP Foundation & Core Pipeline
- **Month 2**: Enhanced Features & Multi-Language Support
- **Month 3**: Advanced Tools & Production Polish
- **Month 4**: Payments, Security & Deployment

## Development Status

🚧 Project in active development

## License

Proprietary - All rights reserved
