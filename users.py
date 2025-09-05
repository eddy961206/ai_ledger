from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..schemas.user import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """현재 사용자 정보 조회"""
    return current_user

