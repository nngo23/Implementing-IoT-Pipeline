
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router as api_v1_router
from app.config import Config
import logging


# Create app
app = FastAPI(
    title=Config.APP_NAME,
    version=Config.VERSION,
    description="AI-powered candidate search using Qdrant + Google Gemini"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_v1_router, prefix=Config.API_V1_PREFIX)

@app.get("/")
async def root():
    return {
        "app": Config.APP_NAME,
        "version": Config.VERSION,
        "docs": "/docs",
        "health": f"{Config.API_V1_PREFIX}/health"
    }