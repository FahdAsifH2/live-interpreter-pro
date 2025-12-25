# Live Interpreter Pro - Frontend

Flutter application for web, iOS, and Android platforms.

## Setup

1. Install Flutter SDK: https://docs.flutter.dev/get-started/install

2. Install dependencies:
```bash
flutter pub get
```

3. Configure API base URL (optional):
```bash
flutter run --dart-define=API_BASE_URL=http://localhost:8000
```

4. Run the app:
```bash
flutter run
```

For web:
```bash
flutter run -d chrome
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

## Configuration

The app connects to the backend API. Make sure the backend is running and accessible.
Default API URL: `http://localhost:8000`

To change the API URL, use:
```bash
flutter run --dart-define=API_BASE_URL=your-api-url
```
