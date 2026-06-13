from fastapi import APIRouter, Depends
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import FAQ, QueryLog, Setting
from ..schemas import BotQuery, BotResponse

router = APIRouter(prefix="/api/bot", tags=["Bot"])


@router.post("/query", response_model=BotResponse)
def bot_query(payload: BotQuery, db: Session = Depends(get_db)):
    query = payload.query.strip()
    faq = (
        db.query(FAQ)
        .filter(FAQ.active.is_(True))
        .filter(or_(func.lower(FAQ.question) == query.lower(), func.lower(FAQ.question).contains(query.lower())))
        .first()
    )
    found = bool(faq)
    answer = faq.answer if faq else "No encontre una respuesta registrada para esa consulta."
    db.add(
        QueryLog(
            telegram_user=payload.telegram_user,
            query_text=query,
            response_text=answer,
            category_id=faq.category_id if faq else None,
        )
    )
    db.commit()
    return BotResponse(answer=answer, found=found)


@router.get("/settings")
def bot_settings(db: Session = Depends(get_db)):
    setting = db.query(Setting).first()
    return {"telegram_chat_id": setting.telegram_chat_id if setting else ""}
