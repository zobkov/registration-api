import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.api.router import api_router
from app.core.config import get_settings
from app.core.rate_limit import limiter


settings = get_settings()
logger = logging.getLogger("registration-api")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.app_name)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.cors_origins],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> JSONResponse:
    return JSONResponse(status_code=200, content={"status": "ok"})


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [err.get("msg", "validation error") for err in exc.errors()]
    return JSONResponse(status_code=400, content={"status": "validation_error", "errors": errors})


@app.exception_handler(ValueError)
async def business_validation_exception_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"status": "validation_error", "errors": [str(exc)]})


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(_: Request, __: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(status_code=429, content={"status": "rate_limited", "errors": ["Too many requests"]})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled server error: %s", type(exc).__name__)
    return JSONResponse(status_code=500, content={"status": "server_error", "errors": ["Internal server error"]})


app.include_router(api_router, prefix=settings.api_prefix)
