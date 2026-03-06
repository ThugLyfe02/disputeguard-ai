from fastapi import FastAPI

from app.api.webhooks import router as webhook_router
from app.api.disputes import router as disputes_router
from app.api.metrics import router as metrics_router
from app.api.fraud_signals import router as fraud_signals_router
from app.api.simulate import router as simulate_router
from app.api.dashboard import router as dashboard_router
from app.api.predictions import router as predictions_router
from app.api.auth import router as auth_router
from app.api.fraud_intelligence import router as fraud_intelligence_router
from app.api.behavior import router as behavior_router

from app.database import engine
from app.models.base import Base


app = FastAPI(title="DisputeGuard AI")


# Create database tables automatically
Base.metadata.create_all(bind=engine)


# Register API routes
app.include_router(webhook_router, prefix="/webhooks")
app.include_router(disputes_router)
app.include_router(metrics_router)
app.include_router(fraud_signals_router)
app.include_router(simulate_router)
app.include_router(dashboard_router)
app.include_router(predictions_router)
app.include_router(auth_router)
app.include_router(fraud_intelligence_router)
app.include_router(behavior_router)


@app.get("/")
def root():
    return {"status": "DisputeGuard AI backend running"}