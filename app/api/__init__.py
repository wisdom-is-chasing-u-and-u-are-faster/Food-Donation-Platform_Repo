from fastapi import APIRouter
from app.api.telemetry import router as telemetry_router
from app.api.donations import router as donations_router
from app.api.matching import router as matching_router
from app.api.dispatch import router as dispatch_router
from app.api.custody import router as custody_router
from app.api.analytics import router as analytics_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(telemetry_router)
api_router.include_router(donations_router)
api_router.include_router(matching_router)
api_router.include_router(dispatch_router)
api_router.include_router(custody_router)
api_router.include_router(analytics_router)

__all__ = ["api_router"]
