import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
import httpx

API_URL = os.getenv("NEXT_PUBLIC_API_URL", "http://backend:8000")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_INTERNAL_TOKEN = os.getenv("BOT_INTERNAL_TOKEN")

bot = Bot(TOKEN)
dp = Dispatcher()


async def api_get_today(user_id: int):
  headers = {"Authorization": f"Bearer {BOT_INTERNAL_TOKEN}"} if BOT_INTERNAL_TOKEN else {}
  async with httpx.AsyncClient(base_url=API_URL, headers=headers, timeout=15) as client:
    r = await client.get("/api/bot/today", params={"user_id": user_id})
    r.raise_for_status()
    return r.json()


async def api_complete_task(user_id: int, task_id: int):
  headers = {"Authorization": f"Bearer {BOT_INTERNAL_TOKEN}"} if BOT_INTERNAL_TOKEN else {}
  async with httpx.AsyncClient(base_url=API_URL, headers=headers, timeout=15) as client:
    r = await client.post(f"/api/bot/complete/{task_id}", params={"user_id": user_id})
    r.raise_for_status()
    return r.json()


async def api_register_telegram(telegram_id: str, name: str, email: str):
  async with httpx.AsyncClient(base_url=API_URL, timeout=15) as client:
    await client.post("/api/telegram/register", json={
      "telegram_id": telegram_id,
      "name": name,
      "email": email
    })


@dp.message(Command("start"))
async def cmd_start(message: Message):
  await message.answer("Привет! Напиши своё имя и e-mail через запятую: Имя, email@example.com")


@dp.message(F.text.contains(","))
async def collect_name_email(message: Message):
  try:
    name, email = [s.strip() for s in message.text.split(",", 1)]
  except Exception:
    await message.answer("Формат: Имя, email@example.com")
    return
  try:
    await api_register_telegram(str(message.from_user.id), name, email)
    await message.answer("Готово! Команды: /help, /today, /progress, /done N")
  except Exception:
    await message.answer("Не удалось зарегистрировать. Попробуйте позже.")


@dp.message(Command("help"))
async def cmd_help(message: Message):
  await message.answer("/start — регистрация\n/today — показать задание\n/done N — отметить выполнение задания N\n/progress — ваш прогресс (через веб)")


@dp.message(Command("today"))
async def cmd_today(message: Message):
  try:
    data = await api_get_today(message.from_user.id)
    await message.answer(f"Сегодня: {data['text']} (id={data['id']})")
  except Exception:
    await message.answer("Не удалось получить задание")


@dp.message(Command("done"))
async def cmd_done(message: Message):
  parts = message.text.strip().split()
  if len(parts) < 2 or not parts[1].isdigit():
    await message.answer("Формат: /done <task_id>")
    return
  task_id = int(parts[1])
  try:
    await api_complete_task(message.from_user.id, task_id)
    await message.answer("Отмечено как выполнено")
  except Exception:
    await message.answer("Не удалось отметить")


@dp.message(Command("progress"))
async def cmd_progress(message: Message):
  await message.answer("Прогресс лучше смотреть в веб-кабинете: http://localhost:3000")


async def main():
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
