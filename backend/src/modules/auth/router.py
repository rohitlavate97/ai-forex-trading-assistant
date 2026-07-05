from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.modules.auth.dependencies import get_current_user, RoleChecker
from src.modules.auth.models import User, UserRole
from src.modules.auth.schemas import Token, UserCreate, UserResponse
from src.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(schema: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    service = AuthService(db)
    return await service.register(schema)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Authenticate credentials and return access + refresh tokens."""
    service = AuthService(db)
    user = await service.authenticate(form_data.username, form_data.password)
    return service.generate_tokens(user)


@router.post("/refresh", response_model=Token)
async def refresh(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    service = AuthService(db)
    return await service.refresh_token(refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve details of the currently authenticated user."""
    return current_user


@router.get("/admin-only", dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
async def admin_only_test():
    """Verify administrator permission (RBAC check)."""
    return {"message": "Access granted: You possess administrative privileges."}
