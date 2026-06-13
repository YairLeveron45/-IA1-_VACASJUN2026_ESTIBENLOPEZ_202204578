from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import AdminUser, Setting
from ..schemas import SettingUpdate

router = APIRouter(prefix="/api/settings", tags=["Configuracion"])


@router.get("")
def api_get_settings(db: Session = Depends(get_db), user: AdminUser = Depends(get_current_user)):
    setting = db.query(Setting).first()
    return setting or Setting(telegram_chat_id="")


@router.put("")
def api_update_settings(payload: SettingUpdate, db: Session = Depends(get_db), user: AdminUser = Depends(get_current_user)):
    setting = db.query(Setting).first()
    if not setting:
        setting = Setting(telegram_chat_id=payload.telegram_chat_id)
        db.add(setting)
    else:
        setting.telegram_chat_id = payload.telegram_chat_id
    db.commit()
    db.refresh(setting)
    return setting
