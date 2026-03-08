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
from app.api.customer_risk import router as customer_risk_router
from app.api.device_risk import router as device_risk_router
from app.api.fraud_ml import router as fraud_ml_router
from app.api.fraud_graph import router as fraud_graph_router
from app.api.fraud_rings import router as fraud_rings_router
from app.api.cross_merchant import router as cross_merchant_router
from app.api.reputation import router as reputation_router
from app.api.feature_store import router as feature_store_router
from app.api.behavioral_biometrics import router as behavioral_router
from app.api.fraud_stream import router as fraud_stream_router

from app.database import engine
from app.models.base import Base


app = FastAPI(title="DisputeGuard AI")


# Automatically create tables
Base.metadata.create_all(bind=engine)


# Register routers
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
app.include_router(customer_risk_router)
app.include_router(device_risk_router)
app.include_router(fraud_ml_router)
app.include_router(fraud_graph_router)
app.include_router(fraud_rings_router)
app.include_router(cross_merchant_router)
app.include_router(reputation_router)
app.include_router(feature_store_router)
app.include_router(behavioral_router)
app.include_router(fraud_stream_router)


@app.get("/")
def root():
    return {"status": "DisputeGuard AI backend running"}