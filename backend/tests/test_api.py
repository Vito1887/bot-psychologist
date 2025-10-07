
def test_register_login_and_task_flow(client):
    # Регистрация
    r = client.post("/api/users/register", json={
        "name": "User1",
        "email": "user1@example.com",
        "password": "pass1234"
    })
    assert r.status_code == 200, r.text
    user = r.json()
    assert user["email"] == "user1@example.com"

    # Логин
    r = client.post("/api/auth/login", json={
        "email": "user1@example.com",
        "password": "pass1234"
    })
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]

    # Получить задание на сегодня (создастся при отсутствии)
    r = client.get("/api/tasks/today", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    task = r.json()
    assert task["status"] == "pending"

    # Отметить выполнение
    r = client.post(f"/api/tasks/complete/{task['id']}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    assert r.json()["success"] is True

    # Прогресс
    r = client.get("/api/progress", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    prog = r.json()
    assert prog["completed"] >= 1


def test_admin_endpoints(client):
    # Логин встроенного админа
    r = client.post("/api/auth/login", json={
        "email": "admin@test.local",
        "password": "adminpass"
    })
    assert r.status_code == 200, r.text
    admin_token = r.json()["access_token"]

    # Список пользователей
    r = client.get("/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200, r.text

    # CRUD упражнений
    r = client.get("/api/admin/exercises", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    before = r.json()

    r = client.post("/api/admin/exercises", params={"text": "Тестовое упражнение"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    after = r.json()
    assert len(after) == len(before) + 1

    r = client.delete(f"/api/admin/exercises/{len(after)-1}", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
