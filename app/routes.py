from fastapi import APIRouter
from app.modules.auth.routes import router as login_router
from app.modules.auth.oauth2 import router as oauth2_router

api_router = APIRouter()

api_router.include_router(login_router, prefix="/auth", tags=["auth"])
api_router.include_router(oauth2_router, prefix="/google", tags=["social"])  # Para OAuth2

