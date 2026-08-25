from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from fastapi import APIRouter, Depends, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_active_user, require_roles
from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    generate_refresh_token_string,
    hash_token,
    decode_token
)
from app.core.exceptions import (
    DuplicateEntityException,
    AuthenticationFailedException,
    EntityNotFoundException,
    PermissionDeniedException
)
from app.models.user import User, UserRole
from app.models.profile import Profile
from app.models.refresh_token import RefreshToken
from app.schemas.user import (
    UserCreate,
    UserRead,
    UserUpdate,
    LoginRequest,
    RefreshTokenRequest,
    LogoutRequest,
    TokenResponse
)
from app.schemas.profile import ProfileUpdate, ProfileRead
from app.schemas.common import ApiResponse

router = APIRouter()


async def _issue_token_pair(user: User, db: AsyncSession) -> TokenResponse:
    """Helper to generate JWT access token and store persistent RefreshToken."""
    # 1. Generate JWT Access Token
    token_payload = {"sub": str(user.id), "role": user.role.value}
    access_token = create_access_token(data=token_payload)

    # 2. Generate and Persist Opaque Cryptographic Refresh Token
    raw_refresh_token = generate_refresh_token_string()
    refresh_hash = hash_token(raw_refresh_token)
    
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=refresh_hash,
        issued_at=datetime.now(timezone.utc),
        expires_at=expires_at,
        is_revoked=False
    )
    db.add(db_refresh_token)
    await db.flush()

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        token_type="bearer",
        user=UserRead.model_validate(user)
    )


@router.post("/register", response_model=ApiResponse[UserRead], status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Registers a new user and creates their associated initial profile."""
    # Prevent public self-registration with administrator privileges
    if user_in.role == UserRole.ADMINISTRATOR:
        raise PermissionDeniedException(
            message="Public self-registration with the Administrator role is forbidden. Administrator accounts must be provisioned by a platform administrator."
        )

    # Check if user already exists
    existing = await db.execute(select(User).where(User.email == user_in.email.lower()))
    if existing.scalar_one_or_none():
        raise DuplicateEntityException(message="A user with this email address already exists")

    # Create User
    new_user = User(
        email=user_in.email.lower(),
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        phone=user_in.phone,
        role=user_in.role,
        is_active=True,
        is_superuser=False
    )
    db.add(new_user)
    await db.flush()

    # Create associated Profile
    new_profile = Profile(
        user_id=new_user.id,
        institution=user_in.institution,
        department=user_in.department,
        designation=user_in.designation,
        country=user_in.country
    )
    db.add(new_profile)
    await db.flush()
    await db.refresh(new_user)

    return ApiResponse(
        success=True,
        data=UserRead.model_validate(new_user),
        message="User account and profile registered successfully"
    )


@router.post("/login", response_model=ApiResponse[TokenResponse], status_code=status.HTTP_200_OK)
async def login_json(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticates a user via JSON, creates a persistent RefreshToken, and returns tokens."""
    result = await db.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.email == login_data.email.lower())
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise AuthenticationFailedException(message="Invalid email or password")

    if not user.is_active:
        raise AuthenticationFailedException(message="User account is deactivated")

    tokens = await _issue_token_pair(user=user, db=db)

    return ApiResponse(
        success=True,
        data=tokens,
        message="Login successful"
    )


@router.post("/login/form", response_model=TokenResponse)
async def login_oauth2_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """OAuth2 form login for Swagger UI."""
    result = await db.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.email == form_data.username.lower())
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise AuthenticationFailedException(message="Invalid email or password")

    if not user.is_active:
        raise AuthenticationFailedException(message="User account is deactivated")

    return await _issue_token_pair(user=user, db=db)


def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@router.post("/refresh", response_model=ApiResponse[TokenResponse], status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_data: Optional[RefreshTokenRequest] = None,
    refresh_token_str: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Exchanges an active persistent refresh token for a new token pair.
    Implements strict token rotation: old token is invalidated immediately upon rotation.
    """
    token_str = (refresh_data.refresh_token if refresh_data else None) or refresh_token_str
    if not token_str:
        raise AuthenticationFailedException(message="Refresh token is required")

    incoming_hash = hash_token(token_str)

    # Query persistent token from database
    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token_hash == incoming_hash)
    )
    stored_token = result.scalar_one_or_none()

    if not stored_token:
        raise AuthenticationFailedException(message="Invalid refresh token")

    if stored_token.is_revoked:
        raise AuthenticationFailedException(message="Refresh token has been revoked")

    now = datetime.now(timezone.utc)
    if ensure_utc(stored_token.expires_at) <= now:
        raise AuthenticationFailedException(message="Refresh token has expired")

    # Fetch User
    user_result = await db.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == stored_token.user_id)
    )
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise AuthenticationFailedException(message="User not found or deactivated")

    # Rotate Token: Invalidate old token
    stored_token.is_revoked = True
    stored_token.revoked_at = now

    # Issue new token pair & save new persistent refresh token
    new_raw_refresh = generate_refresh_token_string()
    new_hash = hash_token(new_raw_refresh)
    stored_token.replaced_by_token_hash = new_hash

    new_db_token = RefreshToken(
        user_id=user.id,
        token_hash=new_hash,
        issued_at=now,
        expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        is_revoked=False
    )
    db.add(new_db_token)
    await db.flush()

    token_payload = {"sub": str(user.id), "role": user.role.value}
    new_access_token = create_access_token(data=token_payload)

    return ApiResponse(
        success=True,
        data=TokenResponse(
            access_token=new_access_token,
            refresh_token=new_raw_refresh,
            token_type="bearer",
            user=UserRead.model_validate(user)
        ),
        message="Token refreshed and rotated successfully"
    )


@router.post("/logout", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def logout(
    logout_data: LogoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logs out the user and revokes the specified persistent refresh token.
    Subsequent attempts to use this refresh token will fail.
    """
    incoming_hash = hash_token(logout_data.refresh_token)

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == incoming_hash,
            RefreshToken.user_id == current_user.id
        )
    )
    stored_token = result.scalar_one_or_none()

    if stored_token and not stored_token.is_revoked:
        stored_token.is_revoked = True
        stored_token.revoked_at = datetime.now(timezone.utc)
        await db.flush()

    return ApiResponse(
        success=True,
        data={"revoked": True},
        message="Logged out successfully and refresh token revoked"
    )


@router.get("/me", response_model=ApiResponse[UserRead], status_code=status.HTTP_200_OK)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves the authenticated user details including their profile."""
    # Ensure profile is loaded
    result = await db.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == current_user.id)
    )
    user_with_profile = result.scalar_one()
    return ApiResponse(
        success=True,
        data=UserRead.model_validate(user_with_profile),
        message="User profile retrieved successfully"
    )


@router.put("/me", response_model=ApiResponse[UserRead], status_code=status.HTTP_200_OK)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Updates user and profile information."""
    result = await db.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == current_user.id)
    )
    user = result.scalar_one()

    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.phone is not None:
        user.phone = user_update.phone
    if user_update.role is not None:
        user.role = user_update.role
    if user_update.password is not None:
        user.hashed_password = get_password_hash(user_update.password)

    # Handle profile updates
    if user_update.profile is not None:
        if not user.profile:
            user.profile = Profile(user_id=user.id)
            db.add(user.profile)
        
        prof_data = user_update.profile
        if prof_data.institution is not None:
            user.profile.institution = prof_data.institution
        if prof_data.department is not None:
            user.profile.department = prof_data.department
        if prof_data.designation is not None:
            user.profile.designation = prof_data.designation
        if prof_data.country is not None:
            user.profile.country = prof_data.country
        if prof_data.bio is not None:
            user.profile.bio = prof_data.bio
        if prof_data.orcid_id is not None:
            user.profile.orcid_id = prof_data.orcid_id
        if prof_data.website is not None:
            user.profile.website = prof_data.website

    await db.flush()
    await db.refresh(user)

    return ApiResponse(
        success=True,
        data=UserRead.model_validate(user),
        message="Profile updated successfully"
    )


# ==============================================================================
# RBAC Test Endpoints (Verifying access control for all 4 roles)
# ==============================================================================

@router.get("/test/researcher-only", response_model=ApiResponse[dict])
async def test_researcher_access(
    current_user: User = Depends(require_roles([UserRole.RESEARCHER]))
):
    return ApiResponse(success=True, data={"role": current_user.role.value, "access": "granted"})


@router.get("/test/founder-only", response_model=ApiResponse[dict])
async def test_founder_access(
    current_user: User = Depends(require_roles([UserRole.STARTUP_FOUNDER]))
):
    return ApiResponse(success=True, data={"role": current_user.role.value, "access": "granted"})


@router.get("/test/manager-only", response_model=ApiResponse[dict])
async def test_manager_access(
    current_user: User = Depends(require_roles([UserRole.INNOVATION_MANAGER]))
):
    return ApiResponse(success=True, data={"role": current_user.role.value, "access": "granted"})


@router.get("/test/admin-only", response_model=ApiResponse[dict])
async def test_admin_access(
    current_user: User = Depends(require_roles([UserRole.ADMINISTRATOR]))
):
    return ApiResponse(success=True, data={"role": current_user.role.value, "access": "granted"})
