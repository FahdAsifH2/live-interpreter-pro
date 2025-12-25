from fastapi import WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.core.database import SessionLocal
from app.models.user import User
from app.models.session import Session as SessionModel
from app.models.transcript import Transcript
from app.services.stt import DeepgramSTTService
from app.services.translation import TranslationService
from app.core.security import decode_token
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)


manager = ConnectionManager()
stt_service = DeepgramSTTService()
translation_service = TranslationService()


async def websocket_interpretation(
    websocket: WebSocket,
    source_language: str = Query(...),
    target_language: str = Query(...),
    token: str = Query(...),
    session_id: Optional[int] = Query(None)
):
    """WebSocket endpoint for real-time interpretation"""
    # Authenticate user
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            await websocket.close(code=1008, reason="Invalid user")
            return
        
        await manager.connect(websocket, user.id)
        
        # Create or get session
        session: Optional[SessionModel] = None
        if session_id:
            session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            session = SessionModel(
                user_id=user.id,
                source_language=source_language,
                target_language=target_language
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        
        if not session:
            await websocket.close(code=1008, reason="Failed to create session")
            return
        
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            
            # Transcribe audio
            transcription_result = await stt_service.transcribe_audio(data, source_language)
            
            if transcription_result and transcription_result.get("text"):
                original_text = transcription_result["text"]
                confidence = transcription_result.get("confidence", 0.0)
                
                # Translate text
                translated_text = await translation_service.translate(
                    original_text,
                    source_language,
                    target_language
                )
                
                # Save transcript
                transcript = Transcript(
                    session_id=session.id,
                    original_text=original_text,
                    translated_text=translated_text,
                    source_language=source_language,
                    target_language=target_language,
                    timestamp=0.0,  # Will be calculated from audio
                    confidence=confidence
                )
                db.add(transcript)
                db.commit()
                
                # Send results to client
                await websocket.send_json({
                    "type": "transcription",
                    "original_text": original_text,
                    "translated_text": translated_text,
                    "confidence": confidence,
                    "timestamp": transcript.created_at.isoformat(),
                })
    
    except WebSocketDisconnect:
        manager.disconnect(user.id)
        # End session
        if session:
            session.ended_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()

