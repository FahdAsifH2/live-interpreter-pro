from fastapi import WebSocket, WebSocketDisconnect, Query
from datetime import datetime
from typing import Optional
from app.core.database import get_supabase_client, Client
from app.services.stt import DeepgramSTTService
from app.services.translation import TranslationService
from app.services.auth.supabase_auth_service import SupabaseAuthService
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}  # Changed to string for UUID
    
    async def connect(self, websocket: WebSocket, user_id: str):
        # Don't accept here - already accepted
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: str):
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
    # Accept connection first (required before any operations)
    await websocket.accept()
    
    print(f"WebSocket connected: source={source_language}, target={target_language}, has_token={bool(token)}")
    
    supabase = get_supabase_client()
    auth_service = SupabaseAuthService(supabase)
    
    try:
        # Verify token with Supabase Auth
        try:
            if not token:
                await websocket.close(code=1008, reason="Token is required")
                return
                
            auth_user = supabase.auth.get_user(token)
            if not auth_user or not auth_user.user:
                print("Auth user not found or invalid")
                await websocket.close(code=1008, reason="Invalid token")
                return
                
            print(f"Auth user verified: {auth_user.user.id}")
        except Exception as auth_error:
            print(f"Auth verification error: {auth_error}")
            import traceback
            traceback.print_exc()
            await websocket.close(code=1008, reason="Incorrect auth token")
            return
        
        user = await auth_service.get_user_by_id(str(auth_user.user.id))
        if not user:
            print(f"User not found in database: {auth_user.user.id}")
            # Try to create user record if it doesn't exist
            try:
                user_data = {
                    "id": str(auth_user.user.id),
                    "email": auth_user.user.email or "",
                    "full_name": auth_user.user.user_metadata.get("full_name") if auth_user.user.user_metadata else None,
                    "is_active": True,
                    "is_verified": auth_user.user.email_confirmed_at is not None,
                    "role": "user"
                }
                result = supabase.table("users").insert(user_data).execute()
                if result.data:
                    user = result.data[0]
                    print(f"Created user record: {user['id']}")
                else:
                    await websocket.close(code=1008, reason="Failed to create user record")
                    return
            except Exception as create_error:
                print(f"Error creating user record: {create_error}")
                await websocket.close(code=1008, reason="User record creation failed")
                return
        
        if not user.get("is_active", True):
            await websocket.close(code=1008, reason="User account is inactive")
            return
        
        print(f"User verified: {user['id']}")
        
        # Add to connection manager (connection already accepted)
        await manager.connect(websocket, user["id"])
        print("Added to connection manager")
        
        # Create or get session
        session = None
        if session_id:
            result = supabase.table("sessions").select("*").eq("id", session_id).execute()
            if result.data:
                session = result.data[0]
                print(f"Using existing session: {session_id}")
        
        if not session:
            # Create new session
            session_data = {
                "user_id": user["id"],
                "source_language": source_language,
                "target_language": target_language,
                "started_at": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            try:
                result = supabase.table("sessions").insert(session_data).execute()
                if result.data:
                    session = result.data[0]
                    print(f"Created new session: {session['id']}")
                else:
                    print("Failed to create session - no data returned")
            except Exception as session_error:
                print(f"Error creating session: {session_error}")
                import traceback
                traceback.print_exc()
        
        if not session:
            await websocket.close(code=1008, reason="Failed to create session")
            return
        
        print("WebSocket ready to receive audio data")
        
        # Send ready message to client
        await websocket.send_json({
            "type": "ready",
            "message": "WebSocket connected and ready for audio",
            "session_id": session["id"]
        })
        
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
                transcript_data = {
                    "session_id": session["id"],
                    "original_text": original_text,
                    "translated_text": translated_text,
                    "source_language": source_language,
                    "target_language": target_language,
                    "timestamp": 0.0,  # Will be calculated from audio
                    "confidence": confidence,
                    "created_at": datetime.utcnow().isoformat()
                }
                supabase.table("transcripts").insert(transcript_data).execute()
                
                # Send results to client
                await websocket.send_json({
                    "type": "transcription",
                    "original_text": original_text,
                    "translated_text": translated_text,
                    "confidence": confidence,
                    "timestamp": datetime.utcnow().isoformat(),
                })
        
    except WebSocketDisconnect:
        if "user" in locals():
            manager.disconnect(user["id"])
        # End session
        if "session" in locals() and session:
            supabase.table("sessions").update({
                "ended_at": datetime.utcnow().isoformat()
            }).eq("id", session["id"]).execute()
    except Exception as e:
        print(f"WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        if "user" in locals():
            manager.disconnect(user["id"])
