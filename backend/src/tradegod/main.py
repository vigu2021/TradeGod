# Configure logging before any other imports so that import-time logs
# (e.g. SQLAlchemy engine setup) flow through the configured pipeline.
from tradegod.core.logging_config import setup_logging
from tradegod.core.middlewares.request_logging import RequestLoggingMiddleware
from tradegod.auth.routes import auth_router
from tradegod.users.routes import users_router

setup_logging()

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from tradegod.core.database import engine
from tradegod.core.error_handlers import (
    app_error_handler,
    http_exception_handler,
    request_validation_handler,
    unhandled_exception_handler,
)
from tradegod.core.exceptions import AppError
from tradegod.core.settings import get_settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Ping the database at initialization
    async with engine.connect() as conn:
        _ = await conn.execute(text("SELECT 1"))
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

# Middlewares
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth_router)
app.include_router(users_router)


# Error handlers
app.add_exception_handler(AppError, app_error_handler)  # pyright: ignore[reportArgumentType]
app.add_exception_handler(RequestValidationError, request_validation_handler)  # pyright: ignore[reportArgumentType]
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # pyright: ignore[reportArgumentType]
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.get("/")
async def root():
    return {"message": "TradeGod API"}


def main():
    uvicorn.run(
        "tradegod.main:app",
        host="127.0.0.1",
        port=get_settings().port,
        reload=True,
    )
