from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import AdminUser, Category, FAQ, QueryLog

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("")
def api_dashboard(db: Session = Depends(get_db), user: AdminUser = Depends(get_current_user)):
    popular = (
        db.query(
            QueryLog.query_text,
            func.max(QueryLog.telegram_user).label("telegram_user"),
            func.count(QueryLog.id).label("total"),
        )
        .group_by(QueryLog.query_text)
        .order_by(func.count(QueryLog.id).desc())
        .all()
    )
    category_stats = (
        db.query(Category.name, func.count(QueryLog.id).label("total"))
        .join(QueryLog, QueryLog.category_id == Category.id)
        .group_by(Category.name)
        .order_by(func.count(QueryLog.id).desc())
        .limit(5)
        .all()
    )
    unique_users = (
        db.query(func.count(func.distinct(QueryLog.telegram_user)))
        .filter(QueryLog.telegram_user != "")
        .scalar()
        or 0
    )
    return {
        "stats": {
            "faqs": db.query(FAQ).count(),
            "categories": db.query(Category).count(),
            "logs": db.query(QueryLog).count(),
            "users": unique_users,
        },
        "popular": [
            {"query_text": row.query_text, "telegram_user": row.telegram_user, "total": row.total}
            for row in popular
        ],
        "category_stats": [{"category": row.name, "total": row.total} for row in category_stats],
    }
