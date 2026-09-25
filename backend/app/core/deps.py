from typing import AsyncGenerator, List, Callable, Optional
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import decode_token
from app.core.exceptions import AuthenticationFailedException, PermissionDeniedException
from app.models.user import User, UserRole
from app.schemas.user import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login/form",
    auto_error=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining an asynchronous database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Validates JWT bearer token and retrieves the authenticated user."""
    if not token:
        raise AuthenticationFailedException(message="Authentication token is missing")

    payload_dict = decode_token(token)
    if not payload_dict:
        raise AuthenticationFailedException(message="Token is invalid or expired")

    token_type = payload_dict.get("type")
    if token_type != "access":
        raise AuthenticationFailedException(message="Invalid token type, access token required")

    user_id = payload_dict.get("sub")
    if not user_id:
        raise AuthenticationFailedException(message="Token payload invalid, missing user identifier")

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationFailedException(message="User associated with token not found")

    if not user.is_active:
        raise AuthenticationFailedException(message="User account is deactivated")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verifies that the current user is active."""
    if not current_user.is_active:
        raise AuthenticationFailedException(message="Inactive user account")
    return current_user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Retrieves user if valid token provided, otherwise returns None without error."""
    if not token:
        return None
    try:
        payload_dict = decode_token(token)
        if not payload_dict or payload_dict.get("type") != "access":
            return None
        user_id = payload_dict.get("sub")
        if not user_id:
            return None
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None



def require_roles(allowed_roles: List[UserRole]) -> Callable:
    """Dependency factory ensuring the user possesses one of the authorized roles."""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.is_superuser:
            return current_user
        if current_user.role not in allowed_roles:
            raise PermissionDeniedException(
                message=f"Access requires one of the following roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker
