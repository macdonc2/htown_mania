from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
import httpx, base64, json
from app.config.settings import Settings
from app.utils.security import create_session_payload

router = APIRouter()
settings = Settings()

@router.get('/auth/login')
async def login(request: Request):
    redirect_uri = f"{settings.app_base_url}/auth/callback"
    params = {
        'client_id': settings.google_client_id,
        'response_type': 'code',
        'scope': 'openid email profile',
        'redirect_uri': redirect_uri,
        'state': 'state',
        'access_type': 'offline',
        'prompt': 'select_account'
    }
    google = 'https://accounts.google.com/o/oauth2/v2/auth'
    url = httpx.URL(google, params=params)
    return RedirectResponse(str(url))

@router.get('/auth/callback')
async def callback(request: Request, code: str | None = None, state: str | None = None):
    if not code:
        raise HTTPException(status_code=400, detail='Missing code')
    token_url = 'https://oauth2.googleapis.com/token'
    redirect_uri = f"{settings.app_base_url}/auth/callback"
    data = {
        'code': code, 'client_id': settings.google_client_id, 'client_secret': settings.google_client_secret,
        'redirect_uri': redirect_uri, 'grant_type': 'authorization_code'
    }
    async with httpx.AsyncClient() as client:
        tr = await client.post(token_url, data=data)
        tr.raise_for_status()
        id_token = tr.json().get('id_token')
        if not id_token: raise HTTPException(status_code=400, detail='No id_token')
        parts = id_token.split('.')
        if len(parts) < 2: raise HTTPException(status_code=400, detail='Invalid id_token')
        payload = parts[1] + '=='
        decoded = json.loads(base64.urlsafe_b64decode(payload).decode('utf-8'))
        email = decoded.get('email')
        if email not in settings.allowed_emails_list:
            raise HTTPException(status_code=403, detail='Email not authorized')
        token = create_session_payload(email)
        resp = RedirectResponse(url='/')
        resp.set_cookie(settings.session_cookie_name, token, httponly=True, samesite='lax')
        return resp
