from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .auth import decode_token
from .database import get_db
from .models import AdminUser


def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> AdminUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")
    username = decode_token(authorization.replace("Bearer ", "", 1))
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")
    user = db.query(AdminUser).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return user
