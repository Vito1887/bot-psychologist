from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .config import settings
from .routers import router
from .scheduler import init_scheduler
from .services import ensure_admin
from .database import SessionLocal

app = FastAPI(title="Psychologist Bot API")

# CORS для фронта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*" if not settings.next_public_api_url else "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    # создать админа
    db = SessionLocal()
    try:
        ensure_admin(db, settings.admin_email, settings.admin_password)
    finally:
        db.close()
    # планировщик
    init_scheduler()


app.include_router(router)
