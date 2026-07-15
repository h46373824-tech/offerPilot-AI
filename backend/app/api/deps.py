from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
Db = Annotated[Session, Depends(get_db)]


def get_current_user(db: Db, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录凭证无效",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = int(decode_token(token).get("sub", ""))
    except (jwt.PyJWTError, ValueError):
        raise credentials_error from None
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_admin(user: CurrentUser) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return user


CurrentAdmin = Annotated[User, Depends(get_current_admin)]
