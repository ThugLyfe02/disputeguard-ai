from fastapi import FastAPI

from app.api.webhooks import router as webhook_router
from app.api.disputes import router as disputes_router
from app.api.metrics import router as metrics_router
from app.api.fraud_signals import router as fraud_signals_router
from app.api.simulate import router as simulate_router

from app.database import engine
from app.models.base import Base


app = FastAPI(title="DisputeGuard AI")


# Automatically create database tables



# Register API routes
app.include_router(webhook_router, prefix="/webhooks")
app.include_router(disputes_router)
app.include_router(metrics_router)
app.include_router(fraud_signals_router)
app.include_router(simulate_router)


@app.get("/")
def root():
    return {"status": "DisputeGuard AI backend running"}
