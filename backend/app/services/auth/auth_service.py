from app.core.security import verify_password, get_password_hash
from app.core.database import Client
from typing import Optional, Dict
from datetime import datetime


class AuthService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    async def create_user(self, email: str, password: str, full_name: Optional[str] = None) -> Dict:
        """Create a new user"""
        hashed_password = get_password_hash(password)
        
        # Check if user already exists
        existing = self.supabase.table("users").select("id").eq("email", email).execute()
        if existing.data:
            raise ValueError("Email already registered")
        
        # Create user
        user_data = {
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "is_active": True,
            "is_verified": False,
            "role": "user",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = self.supabase.table("users").insert(user_data).execute()
        return result.data[0] if result.data else None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        result = self.supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        result = self.supabase.table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    
    async def verify_user_password(self, email: str, password: str) -> Optional[Dict]:
        """Verify user password and return user if valid"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user["hashed_password"]):
            return None
        
        if not user.get("is_active", True):
            return None
        
        return user
    
    async def update_user(self, user_id: int, **updates) -> Dict:
        """Update user information"""
        updates["updated_at"] = datetime.utcnow().isoformat()
        result = self.supabase.table("users").update(updates).eq("id", user_id).execute()
        return result.data[0] if result.data else None
