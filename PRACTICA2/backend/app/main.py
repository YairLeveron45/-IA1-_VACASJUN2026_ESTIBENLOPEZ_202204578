from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .database import Base, engine, get_db
from .routers import admin_users, auth, bot, categories, dashboard, faqs, settings
from .seed import seed_database

app = FastAPI(title="SmartBot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin_users.router)
app.include_router(dashboard.router)
app.include_router(categories.router)
app.include_router(faqs.router)
app.include_router(settings.router)
app.include_router(bot.router)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_query_log_schema()
    db = next(get_db())
    seed_database(db)


def ensure_query_log_schema() -> None:
    with engine.begin() as connection:
        columns = connection.execute(text("PRAGMA table_info(query_logs)")).fetchall()
        column_names = {column[1] for column in columns}
        if "category_id" not in column_names:
            connection.execute(text("ALTER TABLE query_logs ADD COLUMN category_id INTEGER"))


@app.get("/health", tags=["General"])
def health() -> dict[str, str]:
    return {"status": "ok"}
