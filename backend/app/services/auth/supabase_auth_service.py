from app.core.database import Client
from typing import Optional, Dict
from supabase import Client as SupabaseClient


class SupabaseAuthService:
    """Service for Supabase Auth operations"""
    
    def __init__(self, supabase: SupabaseClient):
        self.supabase = supabase
    
    async def sign_up(self, email: str, password: str, full_name: Optional[str] = None) -> Dict:
        """Sign up a new user with Supabase Auth"""
        try:
            # Check if user already exists in our users table
            existing_user = await self.get_user_by_email(email)
            if existing_user:
                raise ValueError("Email already registered. Please login instead.")
            
            # Sign up with Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name or ""
                    }
                }
            })
            
            if not auth_response.user:
                raise ValueError("Failed to create user in Supabase Auth")
            
            # Create user record in our users table
            user_data = {
                "id": str(auth_response.user.id),  # Use Supabase Auth UUID as string
                "email": email,
                "full_name": full_name,
                "is_active": True,
                "is_verified": False,
                "role": "user"
            }
            
            try:
                result = self.supabase.table("users").insert(user_data).execute()
                
                if result.data:
                    return result.data[0]
            except Exception as insert_error:
                # If insert fails due to duplicate key, user might already exist
                # Try to get the existing user
                existing = await self.get_user_by_id(str(auth_response.user.id))
                if existing:
                    raise ValueError("Email already registered. Please login instead.")
                # If it's a different error, re-raise it
                raise ValueError(f"Failed to create user record: {str(insert_error)}")
            
            # If insert fails, return auth user data
            return {
                "id": str(auth_response.user.id),
                "email": email,
                "full_name": full_name,
                "is_active": True,
                "is_verified": False,
                "role": "user"
            }
            
        except ValueError:
            # Re-raise ValueError as-is (these are our custom errors)
            raise
        except Exception as e:
            error_msg = str(e)
            # Check for duplicate key error
            if "duplicate key" in error_msg.lower() or "23505" in error_msg:
                raise ValueError("Email already registered. Please login instead.")
            raise ValueError(f"Failed to sign up: {error_msg}")
    
    async def sign_in(self, email: str, password: str) -> Dict:
        """Sign in user with Supabase Auth"""
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user:
                raise ValueError("Invalid credentials")
            
            # Get user from our users table
            result = self.supabase.table("users").select("*").eq("id", str(auth_response.user.id)).execute()
            
            if result.data:
                user = result.data[0]
                if not user.get("is_active", True):
                    raise ValueError("User account is inactive")
                return {
                    "user": user,
                    "session": auth_response.session
                }
            
            raise ValueError("User not found")
            
        except Exception as e:
            raise ValueError(f"Failed to sign in: {str(e)}")
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by Supabase Auth UUID"""
        # user_id can be UUID string or UUID object
        user_id_str = str(user_id) if user_id else None
        if not user_id_str:
            return None
        result = self.supabase.table("users").select("*").eq("id", user_id_str).execute()
        return result.data[0] if result.data else None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        result = self.supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    
    async def update_user(self, user_id: str, **updates) -> Dict:
        """Update user information"""
        user_id_str = str(user_id) if user_id else None
        if not user_id_str:
            raise ValueError("Invalid user ID")
        result = self.supabase.table("users").update(updates).eq("id", user_id_str).execute()
        return result.data[0] if result.data else None
    
    def get_user_from_token(self, token: str) -> Optional[Dict]:
        """Get user from Supabase Auth token"""
        try:
            # Verify token and get user
            user = self.supabase.auth.get_user(token)
            if user:
                return user.user
            return None
        except Exception:
            return None
