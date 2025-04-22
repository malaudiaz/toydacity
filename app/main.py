from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi
from app.modules.auth.dependencies import get_current_active_user
from fastapi.middleware.cors import CORSMiddleware

from starlette.middleware.sessions import SessionMiddleware

from app  import __version__
from app.core.config import settings
from app.routes import api_router

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="sessionsecret")
app.include_router(api_router, prefix=settings.API_V1_STR)

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
        "https://localhost",
        "https://localhost:8000",
        "https://localhost:3000",    
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": f"Toydacity API version {__version__.__version__}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)