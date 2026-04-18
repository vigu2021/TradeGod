# Configure logging before any other imports so that import-time logs
# (e.g. SQLAlchemy engine setup) flow through the configured pipeline.
from tradegod.core.logging_config import setup_logging
from tradegod.routes.users import users_router

setup_logging()

from contextlib import asynccontextmanager
from sqlalchemy import text
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from tradegod.core.database import engine
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
app.include_router(users_router)


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


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
