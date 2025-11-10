from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.config.settings import Settings
from app.utils.security import verify_session_payload, create_session_payload

settings = Settings()

class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        cookie = request.cookies.get(settings.session_cookie_name)
        if cookie:
            data = verify_session_payload(cookie, settings.session_lifetime_days * 24 * 3600)
            if data:
                request.state.user = data.get('email')
                new_token = create_session_payload(request.state.user)
                response = await call_next(request)
                response.set_cookie(settings.session_cookie_name, new_token, httponly=True, samesite='lax')
                return response
        response = await call_next(request)
        return response
