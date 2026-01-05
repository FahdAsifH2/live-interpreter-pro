from supabase import create_client, Client
from app.core.config import settings
from typing import Optional

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client instance"""
    global _supabase_client
    
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError(
                "Supabase URL and Key must be set in environment variables. "
                "Set SUPABASE_URL and SUPABASE_KEY in your .env file"
            )
        
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY  # Use service role key for backend
        )
    
    return _supabase_client


def get_supabase():
    """Dependency for FastAPI to get Supabase client"""
    return get_supabase_client()
