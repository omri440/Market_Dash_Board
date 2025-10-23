from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.models.user import User
from backend.schemas.user import UserCreate, UserLogin, TokenResponse
from backend.utils.security import hash_password, verify_password
from backend.utils.jwt_handler import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# --- Register ---
@router.post("/register", response_model=TokenResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # לבדוק אם המשתמש כבר קיים
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed = hash_password(user.password)
    # print(hashed)
    new_user = User(
        username=user.username,
        password_hash=hashed,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.username, "role": new_user.role})
    return TokenResponse(access_token=token)


# --- Login ---
@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token({"sub": db_user.username, "role": db_user.role})
    return TokenResponse(access_token=token)
