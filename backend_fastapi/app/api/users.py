from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import json
from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/user")


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    profile = UserResponse.model_validate(current_user)
    return JSONResponse(content={
        "success": True,
        "message": "User profile",
        "data": json.loads(profile.model_dump_json(by_alias=True)),
    })
