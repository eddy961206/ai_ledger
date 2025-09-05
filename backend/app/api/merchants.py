from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..crud import merchant
from ..schemas.merchant import MerchantCreate, MerchantResponse

router = APIRouter()

@router.get("/", response_model=List[MerchantResponse])
def read_merchants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[MerchantResponse]:
    """가맹점 목록 조회"""
    merchants = merchant.get_multi(db, skip=skip, limit=limit)
    return merchants

@router.post("/", response_model=MerchantResponse)
def create_merchant(
    *,
    db: Session = Depends(get_db),
    merchant_in: MerchantCreate,
    current_user: User = Depends(get_current_user),
) -> MerchantResponse:
    """새 가맹점 생성"""
    created_merchant = merchant.create(db, obj_in=merchant_in)
    return created_merchant

@router.get("/{merchant_id}", response_model=MerchantResponse)
def read_merchant(
    *,
    db: Session = Depends(get_db),
    merchant_id: str,
    current_user: User = Depends(get_current_user),
) -> MerchantResponse:
    """특정 가맹점 조회"""
    db_merchant = merchant.get(db, id=merchant_id)
    if not db_merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return db_merchant

