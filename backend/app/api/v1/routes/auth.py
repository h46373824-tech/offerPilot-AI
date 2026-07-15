from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, Db
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas import LoginRequest, Token, UserCreate, UserOut, UserUpdate
from app.services.audit import record_audit

router = APIRouter(prefix="/auth", tags=["身份认证"])


def _authenticate(email: str, password: str, db: Db) -> User:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None or not user.is_active or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Db) -> Token:
    email = payload.email.lower()
    if db.scalar(select(User.id).where(User.email == email)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该邮箱已注册")

    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        hashed_password=hash_password(payload.password),
        is_admin=email in settings.admin_email_set,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该邮箱已注册") from None
    db.refresh(user)
    return Token(access_token=create_access_token(str(user.id)))


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Db) -> Token:
    user = _authenticate(str(payload.email), payload.password, db)
    return Token(access_token=create_access_token(str(user.id)))


@router.post(
    "/token",
    response_model=Token,
    summary="OAuth2 密码登录（供 OpenAPI Authorize 使用）",
)
def oauth2_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Db,
) -> Token:
    user = _authenticate(form.username, form.password, db)
    return Token(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser) -> User:
    return user


@router.patch("/me", response_model=UserOut)
def update_me(payload: UserUpdate, db: Db, user: CurrentUser) -> User:
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(user, key, value)
    record_audit(
        db,
        user_id=user.id,
        action="user.profile_updated",
        entity_type="user",
        entity_id=user.id,
        details={"fields": sorted(changes)},
    )
    db.commit()
    db.refresh(user)
    return user
