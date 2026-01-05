from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_supabase, Client
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.auth.supabase_auth_service import SupabaseAuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, supabase: Client = Depends(get_supabase)):
    """Register a new user with Supabase Auth"""
    auth_service = SupabaseAuthService(supabase)
    
    try:
        user = await auth_service.sign_up(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        # Remove password from response
        user.pop("hashed_password", None)
        return user
    
    except ValueError as e:
        error_message = str(e)
        # Check if it's a duplicate email error
        if "already registered" in error_message.lower() or "duplicate" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_message
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    except Exception as e:
        error_message = str(e)
        if "duplicate key" in error_message.lower() or "23505" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered. Please login instead."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {error_message}"
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, supabase: Client = Depends(get_supabase)):
    """Login with Supabase Auth"""
    auth_service = SupabaseAuthService(supabase)
    
    try:
        result = await auth_service.sign_in(
            email=credentials.email,
            password=credentials.password
        )
        
        if not result or not result.get("session"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        session = result["session"]
        
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: dict,
    supabase: Client = Depends(get_supabase)
):
    """Refresh access token using Supabase Auth refresh token"""
    refresh_token = request.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="refresh_token is required"
        )
    
    try:
        # Refresh session with Supabase Auth
        session = supabase.auth.refresh_session(refresh_token)
        
        if not session or not session.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        return {
            "access_token": session.session.access_token,
            "refresh_token": session.session.refresh_token,
            "token_type": "bearer"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(
    supabase: Client = Depends(get_supabase)
):
    """Logout user (clear Supabase Auth session)"""
    try:
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception:
        return {"message": "Logged out successfully"}
