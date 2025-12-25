from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from app.core.config import settings
from typing import Optional


class DeepgramSTTService:
    def __init__(self):
        self.client = DeepgramClient(settings.DEEPGRAM_API_KEY)
        self.model = settings.DEEPGRAM_MODEL
    
    async def transcribe_audio(self, audio_data: bytes, language: str = "en") -> Optional[dict]:
        """Transcribe audio data using Deepgram"""
        try:
            payload: FileSource = {
                "buffer": audio_data,
            }
            
            options = PrerecordedOptions(
                model=self.model,
                language=language,
                punctuate=True,
                diarize=False,
                smart_format=True,
            )
            
            response = self.client.listen.rest.v("1").transcribe_file(payload, options)
            
            if response.results and response.results.channels:
                channel = response.results.channels[0]
                if channel.alternatives:
                    alternative = channel.alternatives[0]
                    return {
                        "text": alternative.transcript,
                        "confidence": alternative.confidence,
                        "words": [
                            {
                                "word": word.word,
                                "start": word.start,
                                "end": word.end,
                                "confidence": word.confidence,
                            }
                            for word in alternative.words
                        ] if alternative.words else [],
                    }
        except Exception as e:
            print(f"Deepgram transcription error: {e}")
            return None
        
        return None
    
    async def transcribe_stream(self, audio_stream, language: str = "en"):
        """Transcribe streaming audio (for WebSocket)"""
        # This will be implemented for real-time streaming
        # Deepgram supports live transcription via WebSocket
        pass

