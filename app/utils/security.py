from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from typing import Optional
from app.config.settings import Settings
import time

def _ser(secret: str):
    return URLSafeTimedSerializer(secret)

def create_session_payload(email: str) -> str:
    s = Settings()
    ser = _ser(s.session_secret)
    payload = {"email": email, "iat": int(time.time())}
    return ser.dumps(payload)

def verify_session_payload(token: str, max_age: int) -> Optional[dict]:
    s = Settings()
    ser = _ser(s.session_secret)
    try:
        return ser.loads(token, max_age=max_age)
    except (SignatureExpired, BadSignature):
        return None
