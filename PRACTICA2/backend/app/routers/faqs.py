from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import AdminUser, Category, FAQ
from ..schemas import FAQCreate

router = APIRouter(prefix="/api/faqs", tags=["Preguntas frecuentes"])


@router.get("")
def api_list_faqs(db: Session = Depends(get_db), user: AdminUser = Depends(get_current_user)):
    return db.query(FAQ).order_by(FAQ.id.desc()).all()


@router.post("")
def api_create_faq(payload: FAQCreate, db: Session = Depends(get_db), user: AdminUser = Depends(get_current_user)):
    if not db.get(Category, payload.category_id):
        raise HTTPException(status_code=400, detail="Categoria no valida")
    faq = FAQ(**payload.model_dump())
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


@router.put("/{faq_id}")
def api_update_faq(faq_id: int, payload: FAQCreate, db: Session = Depends(get_db), user: AdminUser = Depends(get_current_user)):
    faq = db.get(FAQ, faq_id)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ no encontrada")
    if not db.get(Category, payload.category_id):
        raise HTTPException(status_code=400, detail="Categoria no valida")
    for key, value in payload.model_dump().items():
        setattr(faq, key, value)
    db.commit()
    db.refresh(faq)
    return faq


@router.delete("/{faq_id}")
def api_delete_faq(faq_id: int, db: Session = Depends(get_db), user: AdminUser = Depends(get_current_user)):
    faq = db.get(FAQ, faq_id)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ no encontrada")
    db.delete(faq)
    db.commit()
    return {"deleted": True}
