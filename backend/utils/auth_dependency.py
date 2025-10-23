from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from backend.utils.jwt_handler import verify_access_token
from backend.db import get_db
from backend.models.user import User

security = HTTPBearer()


def get_current_user(
        credentials: HTTPAuthCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user