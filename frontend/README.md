# Live Interpreter Pro - Frontend

Flutter application for web, iOS, and Android platforms.

## Setup

1. Install Flutter SDK: https://docs.flutter.dev/get-started/install

2. Install dependencies:
```bash
flutter pub get
```

3. Run the app:
```bash
flutter run
```

## Project Structure

- `lib/main.dart` - Application entry point
- `lib/core/` - Core configuration, theme, constants
- `lib/features/` - Feature modules (auth, interpretation, glossary, etc.)
- `lib/services/` - API, WebSocket, audio, storage services
- `lib/shared/` - Shared widgets and components
- `lib/router/` - Navigation routing

## Features

- Real-time speech-to-text (Deepgram)
- Real-time translation (DeepL + MS fallback)
- Multi-language support
- Glossary builder
- Vocabulary notebook
- Session transcripts
- Dark mode & Large text mode

