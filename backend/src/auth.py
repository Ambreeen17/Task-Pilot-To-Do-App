import os
from datetime import datetime, timedelta, timezone
from typing import Any

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# passlib bcrypt backend can be flaky on some Windows/Python combos.
# pbkdf2_sha256 is widely supported and avoids bcrypt's 72-byte limit gotchas.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# bcrypt only uses first 72 bytes. We keep a conservative limit to avoid surprises.
MAX_PASSWORD_LEN = 72


def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > MAX_PASSWORD_LEN:
        raise ValueError("Password too long")
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    if len(password.encode("utf-8")) > MAX_PASSWORD_LEN:
        return False
    return pwd_context.verify(password, password_hash)


def create_access_token(*, user_id: str) -> tuple[str, int]:
    expires = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload: dict[str, Any] = {"sub": user_id, "exp": expires}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, int(timedelta(hours=JWT_EXPIRATION_HOURS).total_seconds())


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        raise ValueError("Invalid token") from e
