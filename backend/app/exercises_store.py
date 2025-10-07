import json
import os
from typing import List

DEFAULT_EXERCISES = [
    "5 минут дыхательной практики: вдох 4, задержка 4, выдох 6",
    "Запишите 3 благодарности за сегодня",
    "5 минут осознанного сканирования тела",
    "Короткая прогулка без телефона (10 минут)",
    "Напишите другу тёплое сообщение",
]

STORE_PATH = os.path.join(os.path.dirname(__file__), "exercises.json")


def load_exercises() -> List[str]:
    if not os.path.exists(STORE_PATH):
        save_exercises(DEFAULT_EXERCISES)
        return DEFAULT_EXERCISES
    try:
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [str(x) for x in data]
            return DEFAULT_EXERCISES
    except Exception:
        return DEFAULT_EXERCISES


def save_exercises(items: List[str]) -> None:
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def add_exercise(text: str) -> List[str]:
    items = load_exercises()
    items.append(text)
    save_exercises(items)
    return items


def remove_exercise(index: int) -> List[str]:
    items = load_exercises()
    if 0 <= index < len(items):
        items.pop(index)
        save_exercises(items)
    return items
