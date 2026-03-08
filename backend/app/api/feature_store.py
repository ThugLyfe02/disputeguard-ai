from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.feature_store import get_training_data

router = APIRouter()


@router.get("/fraud/features/training-data")
def training_data(db: Session = Depends(get_db)):

    return get_training_data(db)