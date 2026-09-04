from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.exceptions import (
    DuplicateResourceException,
    UnauthorizedException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_password_hash,
    verify_password,
)
from app.db.seed import seed_demo_data
from app.db.session import get_db
from app.models.user import User, UserSession
from app.schemas.user import (
    Token,
    TokenRefresh,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> Any:
    stmt = select(User).where(User.email == payload.email)
    res = await db.execute(stmt)

    if res.scalar_one_or_none():
        raise DuplicateResourceException(
            resource="User",
            field="email",
        )

    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role="user",
        is_active=True,
        has_onboarded=False,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    user_session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
    )

    db.add(user_session)
    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login", response_model=Token)
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Any:
    stmt = select(User).where(User.email == payload.email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(
        payload.password,
        user.hashed_password,
    ):
        raise UnauthorizedException(
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise UnauthorizedException(
            detail="User account is deactivated"
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    user_session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
    )

    db.add(user_session)
    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/demo-login", response_model=Token)
async def demo_login(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """1-Click instant login for showcases and live demonstrations."""

    user = await seed_demo_data(db)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    user_session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
    )

    db.add(user_session)
    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    payload: TokenRefresh,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Exchange a valid refresh token for a new access token
    and a rotated refresh token.
    """

    # 1. Validate JWT and make sure it is specifically
    #    a refresh token.
    refresh_payload = decode_refresh_token(
        payload.refresh_token
    )

    if refresh_payload is None:
        raise UnauthorizedException(
            detail="Invalid or expired refresh token"
        )

    user_id = refresh_payload["sub"]

    # 2. Find the refresh-token session in the database.
    stmt = select(UserSession).where(
        UserSession.refresh_token == payload.refresh_token
    )

    result = await db.execute(stmt)
    user_session = result.scalar_one_or_none()

    if user_session is None:
        raise UnauthorizedException(
            detail="Refresh session not found"
        )

    # 3. Make sure the session has not already been revoked.
    if user_session.is_revoked:
        raise UnauthorizedException(
            detail="Refresh token has been revoked"
        )

    # 4. Make sure the JWT user and database session user match.
    if user_session.user_id != user_id:
        raise UnauthorizedException(
            detail="Invalid refresh session"
        )

    # 5. Load the user.
    user_stmt = select(User).where(User.id == user_id)

    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedException(
            detail="User not found"
        )

    # 6. Don't issue tokens to inactive accounts.
    if not user.is_active:
        raise UnauthorizedException(
            detail="User account is inactive"
        )

    # 7. Revoke the old refresh-token session.
    #    This prevents reuse of the old refresh token.
    user_session.is_revoked = True

    # 8. Create a new access token.
    new_access_token = create_access_token(user.id)

    # 9. Create a new refresh token.
    new_refresh_token = create_refresh_token(user.id)

    # 10. Store the new refresh-token session.
    new_session = UserSession(
        user_id=user.id,
        refresh_token=new_refresh_token,
    )

    db.add(new_session)

    # 11. Commit both the revocation and new session.
    await db.commit()

    # 12. Return the new token pair.
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
async def logout(
    payload: TokenRefresh,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Revoke the refresh-token session associated
    with the supplied refresh token.
    """

    stmt = select(UserSession).where(
        UserSession.refresh_token == payload.refresh_token
    )

    result = await db.execute(stmt)
    user_session = result.scalar_one_or_none()

    if user_session is None:
        raise UnauthorizedException(
            detail="Refresh session not found"
        )

    # Revoking an already revoked session is harmless,
    # so we simply return success.
    if not user_session.is_revoked:
        user_session.is_revoked = True
        await db.commit()

    return {
        "message": "Logged out successfully"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> Any:
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return current_user
