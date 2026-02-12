from fastapi import APIRouter
from app.schemas.health import HealthCheckResponse
from app.core.vector_search import vector_search
from app.config import Config


router = APIRouter()

@router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():

    qdrant_info = vector_search.get_collection_info()
    

    return {
        "status": "healthy",
        "version": Config.VERSION,
        "qdrant": qdrant_info,
    }