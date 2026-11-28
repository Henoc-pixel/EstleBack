import base64
import hashlib
import hmac
import secrets
import struct
import time
import urllib.parse


def generate_totp_secret() -> str:
    """Génère une clé secrète Base32 compatible Google Authenticator / Authy."""
    raw = secrets.token_bytes(20)
    return base64.b32encode(raw).decode("ascii").rstrip("=")


def _normalize_b32(secret: str) -> bytes:
    cleaned = secret.strip().replace(" ", "").upper()
    pad = (-len(cleaned)) % 8
    return base64.b32decode(cleaned + ("=" * pad), casefold=True)


def get_totp_code(secret: str, for_time: int | None = None, step: int = 30, digits: int = 6) -> str:
    ts = int(time.time()) if for_time is None else int(for_time)
    counter = ts // step
    key = _normalize_b32(secret)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code_int = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code_int % (10**digits)).zfill(digits)


def verify_totp_code(secret: str, code: str, window: int = 1, step: int = 30) -> bool:
    if not secret or not code:
        return False
    cleaned = "".join(ch for ch in code.strip() if ch.isdigit())
    if len(cleaned) != 6:
        return False
    now = int(time.time())
    for drift in range(-window, window + 1):
        expected = get_totp_code(secret, for_time=now + drift * step, step=step)
        if hmac.compare_digest(expected, cleaned):
            return True
    return False


def build_otpauth_uri(email: str, secret: str, issuer: str = "ESTLE") -> str:
    label = urllib.parse.quote(f"{issuer}:{email}")
    params = urllib.parse.urlencode(
        {
            "secret": secret,
            "issuer": issuer,
            "algorithm": "SHA1",
            "digits": "6",
            "period": "30",
        }
    )
    return f"otpauth://totp/{label}?{params}"


def generate_backup_codes(count: int = 6) -> list[str]:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    codes: list[str] = []
    for _ in range(count):
        part1 = "".join(secrets.choice(alphabet) for _ in range(4))
        part2 = "".join(secrets.choice(alphabet) for _ in range(4))
        codes.append(f"{part1}-{part2}")
    return codes
