from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
import os

load_dotenv()  # Carga el .env antes que Pydantic

class Settings(BaseSettings):
    PROJECT_NAME: str = "Toydacity"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_CLIENT_REDIRECT_URI: str = os.getenv("GOOGLE_CLIENT_REDIRECT_URI", "")
       
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://usr:password@localhost:5432/toydacity")
          
    class Config:
        env_file = ".env" 
        env_file_encoding = 'utf-8'

settings = Settings()
