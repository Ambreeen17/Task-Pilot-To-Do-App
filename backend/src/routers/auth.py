from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..auth import create_access_token, hash_password, verify_password
from ..database import get_session
from ..models.user import User
from ..schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_session)) -> UserResponse:
    existing = db.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id, email=user.email, full_name=user.full_name, created_at=user.created_at
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_session)) -> TokenResponse:
    user = db.exec(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token, expires_in = create_access_token(user_id=str(user.id))
    return TokenResponse(
        access_token=token, token_type="bearer", expires_in=expires_in, user_name=user.full_name
    )
