# Configure logging before any other imports so that import-time logs
# (e.g. SQLAlchemy engine setup) flow through the configured pipeline.
from tradegod.logging_config import setup_logging

setup_logging()

from contextlib import asynccontextmanager
from sqlalchemy import text
import uvicorn
from fastapi import FastAPI

from tradegod.database import engine
from tradegod.settings import get_settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Ping the database at initialization
    async with engine.connect() as conn:
        _ = await conn.execute(text("SELECT 1"))
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


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
