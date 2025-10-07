from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import User, Task, TaskStatus
from .security import get_password_hash
from .exercises_store import load_exercises


DEFAULT_TASKS = [
    "5 минут дыхательной практики: вдох 4, задержка 4, выдох 6",
    "Запишите 3 благодарности за сегодня",
    "5 минут осознанного сканирования тела",
    "Короткая прогулка без телефона (10 минут)",
    "Напишите другу тёплое сообщение",
]


def ensure_admin(db: Session, admin_email: str, admin_password: str) -> User:
    user = db.query(User).filter(User.email == admin_email).first()
    if user:
        return user
    user = User(
        name="Admin",
        email=admin_email,
        password_hash=get_password_hash(admin_password),
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_user(db: Session, name: str, email: str, password: Optional[str] = None, telegram_id: Optional[str] = None) -> User:
    user = User(name=name, email=email, telegram_id=telegram_id)
    if password:
        user.password_hash = get_password_hash(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_telegram_user(db: Session, telegram_id: str, name: str, email: str) -> User:
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        if user.name != name or user.email != email:
            user.name = name
            user.email = email
            db.commit()
            db.refresh(user)
        return user
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        existing.telegram_id = telegram_id
        db.commit()
        db.refresh(existing)
        return existing
    return create_user(db, name=name, email=email, telegram_id=telegram_id)


def get_today_task(db: Session, user_id: int) -> Optional[Task]:
    today = datetime.now(timezone.utc).date()
    return (
        db.query(Task)
        .filter(Task.user_id == user_id)
        .filter(func.date(Task.sent_at) == today)
        .order_by(Task.id.desc())
        .first()
    )


def create_daily_task(db: Session, user: User, text: Optional[str] = None) -> Task:
    if not text:
        exercises = load_exercises() or DEFAULT_TASKS
        count = db.query(Task).filter(Task.user_id == user.id).count()
        text = exercises[count % len(exercises)]
    task = Task(user_id=user.id, text=text)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def mark_task_completed(db: Session, user_id: int, task_id: int) -> Optional[Task]:
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        return None
    task.status = TaskStatus.completed.value
    db.commit()
    db.refresh(task)
    return task


def get_progress(db: Session, user_id: int):
    total = db.query(Task).filter(Task.user_id == user_id).count()
    completed = db.query(Task).filter(Task.user_id == user_id, Task.status == TaskStatus.completed.value).count()

    now = datetime.now(timezone.utc)
    today = now.date()
    start_week = (now - timedelta(days=now.weekday())).date()
    start_month = now.replace(day=1).date()

    today_completed = (
        db.query(Task)
        .filter(Task.user_id == user_id, Task.status == TaskStatus.completed.value)
        .filter(func.date(Task.sent_at) == today)
        .count()
    )
    week_completed = (
        db.query(Task)
        .filter(Task.user_id == user_id, Task.status == TaskStatus.completed.value)
        .filter(func.date(Task.sent_at) >= start_week)
        .count()
    )
    month_completed = (
        db.query(Task)
        .filter(Task.user_id == user_id, Task.status == TaskStatus.completed.value)
        .filter(func.date(Task.sent_at) >= start_month)
        .count()
    )

    return {
        "total": total,
        "completed": completed,
        "today_completed": today_completed,
        "week_completed": week_completed,
        "month_completed": month_completed,
    }


def list_tasks_for_user(db: Session, user_id: int):
    return db.query(Task).filter(Task.user_id == user_id).order_by(Task.sent_at.desc()).all()
