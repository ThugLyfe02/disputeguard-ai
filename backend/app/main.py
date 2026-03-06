from fastapi import FastAPI
from app.api.webhooks import router as webhook_router

from fastapi import FastAPI

app = FastAPI(title="DisputeGuard AI")

app.include_router(webhook_router, prefix="/webhooks")

@app.get("/")
def root():
    return {"status": "DisputeGuard AI backend running"}
