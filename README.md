# Бот-психолог

Минимальный продукт: Telegram-бот + Backend (FastAPI) + Web (Next.js), разворачивается через docker compose.

## Быстрый старт

1. Скопируйте `.env.example` в `.env` и заполните значения:
   - `DATABASE_URL` (оставьте по умолчанию для docker)
   - `JWT_SECRET_KEY` (случайная строка)
   - `ADMIN_EMAIL`, `ADMIN_PASSWORD` (будет создан админ)
   - `TELEGRAM_BOT_TOKEN` (токен @BotFather)
   - `BOT_INTERNAL_TOKEN` (случайная строка для bot-эндпоинтов)
   - `NEXT_PUBLIC_API_URL` = `http://localhost:8000`
2. Запустите:

```bash
docker compose up --build
```

3. Backend: `http://localhost:8000` (Swagger: `/docs`).
4. Web: `http://localhost:3000`.

## Функциональность

- Регистрация/вход на вебе. JWT сохраняется в Cookie, дублируем в localStorage для фронта.
- «Текущее задание» и «История». Прогресс: день/неделя/месяц.
- Админ-панель: пользователи, их задания, CRUD упражнений, принудительная генерация задания.
- Планировщик (09:00): создаёт задания на день, шлёт текст в Telegram, если привязан `telegram_id`.

## Бот

Команды: `/start`, `/today`, `/done <task_id>`, `/help`.

- `/start`: отправьте "Имя, email@example.com" — привязка к вашему аккаунту (или создание нового).
- `/today`: получить сегодняшнее задание.
- `/done id`: отметить выполнение.
- `/progress`: смотреть в веб-кабинете.

## Разработка

- Миграции не требуются в MVP: модели создаются на старте.
- Стэк: FastAPI, SQLAlchemy, APScheduler, Next.js, aiogram.

## Тесты

Базовые тесты лежат в `backend/tests` и запускаются локально:

```bash
pip install -r backend/requirements.txt -r backend/requirements.dev.txt
pytest -q backend/tests
```

Примечание: тесты используют in-memory SQLite и переопределяют зависимости БД приложения, таблицы создаются автоматически.
