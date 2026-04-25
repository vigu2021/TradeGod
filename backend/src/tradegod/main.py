# Configure logging before any other imports so that import-time logs
# (e.g. SQLAlchemy engine setup) flow through the configured pipeline.
from tradegod.core.logging_config import setup_logging
from tradegod.core.middlewares.request_logging import RequestLoggingMiddleware
from tradegod.routes.users import users_router

setup_logging()

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT

from tradegod.core.database import engine
from tradegod.core.exceptions import AppError
from tradegod.core.settings import Environment, get_settings


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


# Routers
app.include_router(users_router)


# Errors
@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """Translate Pydantic validation failures into safe 422 responses.

    In non-dev environments, strips the `input` field from each error so
    raw submitted values (e.g. passwords) never leak back to the client.
    In dev, the full detail is returned to aid debugging.
    """
    exclude: set[str] = set() if get_settings().environment == Environment.DEV else {"input"}
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": jsonable_encoder(exc.errors(), exclude=exclude)},
    )


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
