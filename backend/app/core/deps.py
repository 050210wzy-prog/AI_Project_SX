from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import User

ROLE_PERMISSIONS = {
    "admin": ["dashboard", "admissions", "website", "crawler", "innovation", "tickets", "students", "academic", "settings", "users"],
    "admission": ["dashboard", "admissions", "tickets", "students"],
    "editor": ["dashboard", "website", "crawler"],
    "reviewer": ["dashboard", "website"],
    "teacher": ["dashboard", "students", "academic"],
    "operator": ["dashboard", "innovation", "settings", "crawler"],
    "user": [],
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已失效") from exc
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已停用")
    return user


def permission_from_path(path: str) -> str:
    parts = [part for part in path.split("/") if part]
    try:
        marker = parts.index("admin")
        module = parts[marker + 1]
    except (ValueError, IndexError):
        return "dashboard"
    if module in {"dashboard"}:
        return "dashboard"
    if module in {"tickets", "admin-notices"}:
        return "tickets"
    if module in {"site", "knowledge", "upload", "resources"}:
        return "website"
    if module in {"system-configs", "operation-logs", "health-check"}:
        return "settings"
    if module in {"students"}:
        return "students"
    if module in {"academic"}:
        return "academic"
    if module in {"crawl"}:
        return "crawler"
    if module in {"innovation-configs"}:
        return "innovation"
    return module


def get_current_admin(request: Request, user: User = Depends(get_current_user)) -> User:
    permission = permission_from_path(request.url.path)
    allowed = ROLE_PERMISSIONS.get(user.role, [])
    if user.role != "admin" and permission not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有当前模块权限")
    return user


def require_permission(permission: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        allowed = ROLE_PERMISSIONS.get(user.role, [])
        if user.role != "admin" and permission not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有当前模块权限")
        return user

    return checker
