import datetime
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from ninja.errors import HttpError
from ninja.security import HttpBearer
from .models import AuditLog

User = get_user_model()
JWT_ALGORITHM = "HS256"


def create_token(
    user_id: int,
    token_type: str = "access",
    expires_delta: datetime.timedelta | None = None,
) -> str:
    if expires_delta is None:
        if token_type == "access":
            expires_delta = datetime.timedelta(hours=12)
        elif token_type == "2fa_temp":
            expires_delta = datetime.timedelta(minutes=5)
        else:
            expires_delta = datetime.timedelta(days=14)

    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "user_id": user_id,
        "token_type": token_type,
        "exp": now + expires_delta,
        "iat": now,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def require_permission(user, perm_code: str) -> None:
    if not user or not user.has_estle_perm(perm_code):
        raise HttpError(403, f"Permission requise : {perm_code}")


async def record_audit(
    actor,
    action: str,
    summary: str,
    target_type: str = "",
    target_id: str = "",
    metadata: dict | None = None,
) -> None:
    try:
        await AuditLog.objects.acreate(
            actor=actor if getattr(actor, "id", None) else None,
            actor_email=getattr(actor, "email", "") or "system",
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id else "",
            summary=summary[:300],
            metadata=metadata or {},
        )
    except Exception:
        pass


async def create_notification(
    audience: str,
    title: str,
    message: str,
    category: str = "SYSTEM",
    link: str = "",
    recipient_id: Optional[int] = None,
    required_permission: str = "",
):
    from .models import Notification

    try:
        await Notification.objects.acreate(
            audience=audience,
            recipient_id=recipient_id,
            required_permission=required_permission,
            category=category,
            title=title[:180],
            message=message,
            link=link[:255],
        )
    except Exception:
        pass


class AsyncAuthBearer(HttpBearer):
    async def authenticate(self, request, token: str):
        payload = decode_token(token)
        if not payload or payload.get("token_type") != "access":
            return None
        user_id = payload.get("user_id")
        try:
            user = await User.objects.select_related("role").aget(id=user_id, is_active=True)
            request.user = user
            return user
        except User.DoesNotExist:
            return None


class AsyncAdminAuthBearer(HttpBearer):
    async def authenticate(self, request, token: str):
        payload = decode_token(token)
        if not payload or payload.get("token_type") != "access":
            return None
        user_id = payload.get("user_id")
        try:
            user = await User.objects.select_related("role").aget(id=user_id, is_active=True)
            if not (user.is_staff or user.is_superuser or user.account_type == "COLLABORATOR"):
                return None
            request.user = user
            return user
        except User.DoesNotExist:
            return None
