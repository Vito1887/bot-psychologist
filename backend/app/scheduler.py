from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from .database import SessionLocal
from .config import settings
from .models import User
from .services import get_today_task, create_daily_task
import httpx


scheduler: BackgroundScheduler | None = None


def send_telegram_message(telegram_id: str, text: str):
    if not settings.telegram_bot_token or not telegram_id:
        return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        with httpx.Client(timeout=10) as client:
            client.post(url, json={"chat_id": telegram_id, "text": text})
    except Exception:
        pass


def send_daily_tasks():
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            task = get_today_task(db, user.id)
            if not task:
                task = create_daily_task(db, user)
                if user.telegram_id:
                    send_telegram_message(user.telegram_id, f"Ваше задание на сегодня: {task.text}")
    finally:
        db.close()


def init_scheduler():
    global scheduler
    if scheduler:
        return scheduler
    scheduler = BackgroundScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_daily_tasks, CronTrigger(hour=settings.bot_daily_hour, minute=0))
    scheduler.start()
    return scheduler
