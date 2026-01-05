from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_supabase, Client
from app.api.dependencies import get_current_active_user
from app.schemas.user import UserResponse, UserUpdate
from app.services.auth.supabase_auth_service import SupabaseAuthService
from typing import Dict

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Dict = Depends(get_current_active_user)):
    """Get current user profile"""
    # Remove password from response
    user = current_user.copy()
    user.pop("hashed_password", None)
    return user


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    current_user: Dict = Depends(get_current_active_user),
    supabase: Client = Depends(get_supabase)
):
    """Update current user profile"""
    from app.core.security import get_password_hash
    
    auth_service = SupabaseAuthService(supabase)
    updates = {}
    
    if user_update.email:
        # Check if email is already taken
        existing = await auth_service.get_user_by_email(user_update.email)
        if existing and existing["id"] != current_user["id"]:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        updates["email"] = user_update.email
    
    if user_update.full_name is not None:
        updates["full_name"] = user_update.full_name
    
    if user_update.password:
        updates["hashed_password"] = get_password_hash(user_update.password)
    
    if updates:
        updated_user = await auth_service.update_user(current_user["id"], **updates)
        updated_user.pop("hashed_password", None)
        return updated_user
    
    # Return current user if no updates
    user = current_user.copy()
    user.pop("hashed_password", None)
    return user

