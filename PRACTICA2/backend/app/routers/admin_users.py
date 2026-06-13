from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import hash_password
from ..database import get_db
from ..dependencies import get_current_user
from ..models import AdminUser
from ..schemas import AdminUserCreate

router = APIRouter(prefix="/api/admin-users", tags=["Administradores"])


@router.get("")
def api_list_admin_users(db: Session = Depends(get_db), user: AdminUser = Depends(get_current_user)):
    users = db.query(AdminUser).order_by(AdminUser.username).all()
    return [{"id": admin.id, "username": admin.username} for admin in users]


@router.post("", status_code=status.HTTP_201_CREATED)
def api_create_admin_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    user: AdminUser = Depends(get_current_user),
):
    username = payload.username.strip()
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="El usuario debe tener al menos 3 caracteres")
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="La contrasena debe tener al menos 8 caracteres")

    admin = AdminUser(username=username, password_hash=hash_password(payload.password))
    db.add(admin)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="El usuario administrador ya existe") from exc
    db.refresh(admin)
    return {"id": admin.id, "username": admin.username}
