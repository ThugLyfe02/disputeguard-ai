from fastapi import FastAPI

from app.api.webhooks import router as webhook_router
from app.api.disputes import router as disputes_router

from app.database import engine
from app.models.base import Base


app = FastAPI(title="DisputeGuard AI")


# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)


# Register webhook routes
app.include_router(webhook_router, prefix="/webhooks")


# Register dispute API routes
app.include_router(disputes_router)


@app.get("/")
def root():
    return {"status": "DisputeGuard AI backend running"}
