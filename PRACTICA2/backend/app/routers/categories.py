from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import AdminUser, Category
from ..schemas import CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/api/categories", tags=["Categorias"])


@router.get("")
def api_list_categories(db: Session = Depends(get_db), user: AdminUser = Depends(get_current_user)):
    return db.query(Category).order_by(Category.name).all()


@router.post("")
def api_create_category(payload: CategoryCreate, db: Session = Depends(get_db), user: AdminUser = Depends(get_current_user)):
    category = Category(name=payload.name, description=payload.description)
    db.add(category)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="La categoria ya existe") from exc
    db.refresh(category)
    return category


@router.put("/{category_id}")
def api_update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    user: AdminUser = Depends(get_current_user),
):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    category.name = payload.name
    category.description = payload.description
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="La categoria ya existe") from exc
    db.refresh(category)
    return category


@router.delete("/{category_id}")
def api_delete_category(category_id: int, db: Session = Depends(get_db), user: AdminUser = Depends(get_current_user)):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    if category.faqs:
        raise HTTPException(status_code=400, detail="No se puede eliminar una categoria con preguntas")
    db.delete(category)
    db.commit()
    return {"deleted": True}
