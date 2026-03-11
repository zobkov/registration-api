from fastapi import APIRouter

from app.api.v1.registrations import router as registrations_router


api_router = APIRouter()
api_router.include_router(registrations_router, prefix="/registrations", tags=["registrations"])
