import datetime
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from ninja.security import HttpBearer

User = get_user_model()
JWT_ALGORITHM = "HS256"


def create_token(user_id: int, token_type: str = "access", expires_delta: datetime.timedelta | None = None) -> str:
    if expires_delta is None:
        if token_type == "access":
            expires_delta = datetime.timedelta(hours=12)
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


class AsyncAuthBearer(HttpBearer):
    async def authenticate(self, request, token: str):
        payload = decode_token(token)
        if not payload or payload.get("token_type") != "access":
            return None
        user_id = payload.get("user_id")
        try:
            user = await User.objects.aget(id=user_id, is_active=True)
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
            user = await User.objects.aget(id=user_id, is_active=True, is_staff=True)
            request.user = user
            return user
        except User.DoesNotExist:
            return None
