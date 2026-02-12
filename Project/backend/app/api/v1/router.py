from fastapi import APIRouter
from app.api.v1.endpoints import search, health, feedback

router = APIRouter()

# Include endpoints
router.include_router(search.router)
router.include_router(health.router)
router.include_router(feedback.router)
