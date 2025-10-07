from fastapi import APIRouter, Depends, HTTPException, status, Response, Header
from sqlalchemy.orm import Session

from .database import get_db
from . import schemas
from .models import User, Task
from .security import verify_password, create_access_token, get_current_user, require_admin
from .services import create_user, get_today_task, mark_task_completed, get_progress, list_tasks_for_user, create_daily_task, get_or_create_telegram_user
from .exercises_store import load_exercises, add_exercise, remove_exercise
from .config import settings

router = APIRouter(prefix="/api")


@router.post("/users/register", response_model=schemas.UserResponse)
def register_user(payload: schemas.UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already used")
    user = create_user(db, name=payload.name, email=payload.email, password=payload.password)
    return user


@router.post("/auth/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    token = create_access_token(subject=user.email)
    response.set_cookie("access_token", token, httponly=True, samesite="lax")
    return {"access_token": token, "token_type": "bearer"}


@router.get("/tasks/today", response_model=schemas.TaskResponse)
def get_today(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = get_today_task(db, user.id)
    if not task:
        # если задание ещё не создано сегодня — создадим
        task = create_daily_task(db, user)
    return task


@router.get("/tasks", response_model=list[schemas.TaskResponse])
def list_tasks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_tasks_for_user(db, user.id)


@router.post("/tasks/complete/{task_id}", response_model=schemas.CompleteTaskResponse)
def complete_task(task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = mark_task_completed(db, user.id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True, "task": task}


@router.get("/progress", response_model=schemas.ProgressResponse)
def progress(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_progress(db, user.id)


# Админ: пользователи, их задачи, упражнения
@router.get("/admin/users", response_model=list[schemas.UserResponse])
def admin_users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/admin/users/{user_id}/tasks", response_model=list[schemas.TaskResponse])
def admin_user_tasks(user_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    return list_tasks_for_user(db, user_id)


@router.get("/admin/exercises", response_model=list[str])
def admin_list_exercises(_: User = Depends(require_admin)):
    return load_exercises()


@router.post("/admin/exercises", response_model=list[str])
def admin_add_exercise(text: str, _: User = Depends(require_admin)):
    return add_exercise(text)


@router.delete("/admin/exercises/{index}", response_model=list[str])
def admin_delete_exercise(index: int, _: User = Depends(require_admin)):
    return remove_exercise(index)


@router.post("/admin/generate_today/{user_id}")
def admin_generate_today(user_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    task = create_daily_task(db, user)
    return {"task_id": task.id}


@router.post("/bot/complete/{task_id}")
def bot_complete_task(task_id: int, user_id: int, authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    if not settings.bot_internal_token or authorization != f"Bearer {settings.bot_internal_token}":
        raise HTTPException(status_code=401, detail="Unauthorized bot")
    task = mark_task_completed(db, user_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}


@router.get("/bot/today")
def bot_get_today(user_id: int, authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    if not settings.bot_internal_token or authorization != f"Bearer {settings.bot_internal_token}":
        raise HTTPException(status_code=401, detail="Unauthorized bot")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    task = get_today_task(db, user.id)
    if not task:
        task = create_daily_task(db, user)
    return {"id": task.id, "text": task.text, "status": task.status}


@router.post("/telegram/register", response_model=schemas.UserResponse)
def telegram_register(payload: schemas.UserRegisterTelegramRequest, db: Session = Depends(get_db)):
    user = get_or_create_telegram_user(db, telegram_id=payload.telegram_id, name=payload.name, email=payload.email)
    return user
