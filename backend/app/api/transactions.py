from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..crud import transaction
from ..schemas.transaction import TransactionCreate, TransactionResponse

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
def read_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TransactionResponse]:
    """사용자의 거래 내역 조회"""
    transactions = transaction.get_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return transactions

@router.post("/", response_model=TransactionResponse)
def create_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_in: TransactionCreate,
    current_user: User = Depends(get_current_user),
) -> TransactionResponse:
    """새 거래 내역 생성"""
    created_transaction = transaction.create_with_user(db, obj_in=transaction_in, user_id=current_user.id)
    return created_transaction

@router.get("/{transaction_id}", response_model=TransactionResponse)
def read_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_id: str,
    current_user: User = Depends(get_current_user),
) -> TransactionResponse:
    """특정 거래 내역 조회"""
    db_transaction = transaction.get(db, id=transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if db_transaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db_transaction

