import uuid
import secrets
from fastapi import Depends, APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
import httpx
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth

from app.modules.auth import schemas, crud
from app.database import get_db
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

# Configuración OAuth
oauth = OAuth()

# Configurar proveedores OAuth
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_user_by_email(db, email)
    
    if not user:
        return False
    if not user.hashed_password or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def create_refresh_token(db: Session, user_id: int, expires_delta: Optional[timedelta] = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Generar un token único
    refresh_token_data = {
        "sub": str(user_id),
        "exp": expire,
        "jti": str(uuid.uuid4())
    }
    refresh_token = jwt.encode(
        refresh_token_data, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    # Guardar en base de datos
    refresh_token_db = schemas.RefreshTokenCreate(
        user_id=user_id,
        token=refresh_token,
        expires_at=expire
    )
    crud.create_refresh_token(db, refresh_token_db)
    
    return refresh_token

async def verify_refresh_token(db: Session, token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        # Verificar en base de datos
        db_token = crud.get_refresh_token(db, token=token)
        if not db_token or db_token.expires_at < datetime.utcnow() or not db_token.is_active:
            return None
        
        return schemas.TokenData(email=None, user_id=user_id)  # Podrías devolver más datos si necesitas
    except JWTError:
        return None


# Rutas para autenticación social
@router.get("/login")
async def login_google(request: Request):
    
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "scope=openid%20email%20profile&"
        "access_type=offline&"
        "response_type=code&"
        "client_id={settings.GOOGLE_CLIENT_ID}&"
        "redirect_uri={settings.GOOGLE_CLIENT_REDIRECT_URI}"
    )
    
    return RedirectResponse(url=google_auth_url)

@router.get("/callback", response_model=schemas.Token)
async def auth_google(code: str, db: Session = Depends(get_db)):
    toke_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_CLIENT_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(toke_url, data=data)
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Error al obtener el token")
        
    tokes = token_response.json()
    access_token = tokes['access_token']
    
    # Obtener información del usuario
    userinfo_respose = await client.get("https://openidconnect.googleapis.com/v1/userinfo", headers={'Authorization': f'Bearer {access_token}'})


    user_info = userinfo_respose.json()

    # Crear el JWT para el usuario
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) 
    jwt_data = {
        "sub": user_info['sub'],
        "email": user_info['email'],
        "name": user_info['name'],
        "picture": user_info['picture'],
        "exp": expire
    }

    jwt_token = jwt.encode(jwt_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # Crear el token de refresco
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = await create_refresh_token(
        db=db,
        user_id=user_info['sub'],
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }
