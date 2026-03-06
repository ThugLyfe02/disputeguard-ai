from fastapi import APIRouter
from app.services.auth_service import create_access_token

router = APIRouter()


@router.post("/auth/login")
def login():

    # Temporary placeholder login
    merchant_id = 1

    token = create_access_token(merchant_id)

    return {"access_token": token}
