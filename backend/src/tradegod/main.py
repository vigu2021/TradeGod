import uvicorn
from fastapi import FastAPI
from .settings import get_settings

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "TradeGod API"}


def main():
    uvicorn.run(
        "tradegod.main:app", host="127.0.0.1", port=get_settings().port, reload=True
    )
