from fastapi import APIRouter
from app.schemas.dashboard import ApiResponse

router = APIRouter()


@router.get("/health", response_model=ApiResponse[None])
def health():
    return ApiResponse.ok("NyayaAI backend is running")
