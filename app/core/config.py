from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()  # Carga el .env antes que Pydantic

class Settings(BaseSettings):
    PROJECT_NAME: str = "Toydacity"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default="S3cr3t_K3y")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = Field(default="925708649710-pjq0tnkq6qrrqjm6dqprj5moja1oa4v0.apps.googleusercontent.com")
    GOOGLE_CLIENT_SECRET: str = Field(default="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")
    GOOGLE_CLIENT_REDIRECT_URI: str = Field(default="http://127.0.0.1:8000/api/v1/google/callback")
       
    # Database
    DATABASE_URL: str = "postgresql://admin:pgsql09@localhost:5432/toydacity"
          
    class Config:
        env_file = ".env" 
        env_file_encoding = 'utf-8'

settings = Settings()
