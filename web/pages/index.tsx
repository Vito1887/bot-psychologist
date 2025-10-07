import { useEffect, useState } from "react";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [task, setTask] = useState<any>(null);
  const [token, setToken] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [progress, setProgress] = useState<any>(null);

  const register = async () => {
    try {
      await axios.post(`${API_URL}/api/users/register`, {
        name,
        email,
        password,
      });
      setMessage("Регистрация успешна. Теперь войдите.");
    } catch (e: any) {
      setMessage(e?.response?.data?.detail || "Ошибка регистрации");
    }
  };

  const login = async () => {
    try {
      const { data } = await axios.post(
        `${API_URL}/api/auth/login`,
        { email, password },
        { withCredentials: true }
      );
      setToken(data.access_token);
      if (typeof window !== "undefined") {
        localStorage.setItem("token", data.access_token);
      }
      setMessage("Вход выполнен");
    } catch (e: any) {
      setMessage(e?.response?.data?.detail || "Ошибка входа");
    }
  };

  const loadToday = async () => {
    try {
      const { data } = await axios.get(`${API_URL}/api/tasks/today`, {
        withCredentials: true,
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      setTask(data);
    } catch (e: any) {
      setTask(null);
    }
  };

  const loadProgress = async () => {
    try {
      const { data } = await axios.get(`${API_URL}/api/progress`, {
        withCredentials: true,
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      setProgress(data);
    } catch (e: any) {
      setProgress(null);
    }
  };

  const complete = async (id: number) => {
    try {
      await axios.post(
        `${API_URL}/api/tasks/complete/${id}`,
        {},
        {
          withCredentials: true,
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );
      setMessage("Задание выполнено");
      loadToday();
      loadProgress();
    } catch (e: any) {
      setMessage("Ошибка отметки");
    }
  };

  useEffect(() => {
    if (!token && typeof window !== "undefined") {
      const t = localStorage.getItem("token");
      if (t) setToken(t);
    }
  }, []);

  useEffect(() => {
    if (token) {
      loadToday();
      loadProgress();
    }
  }, [token]);

  return (
    <div style={{ padding: 24, fontFamily: "sans-serif", maxWidth: 680 }}>
      <h1>Психолог-бот</h1>
      <p>{message}</p>

      <h2>Регистрация</h2>
      <input
        placeholder="Имя"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <input
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        placeholder="Пароль"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={register}>Зарегистрироваться</button>

      <h2>Вход</h2>
      <input
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        placeholder="Пароль"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={login}>Войти</button>

      <div style={{ marginTop: 12 }}>
        <a href="/history">История заданий</a> |{" "}
        <a href="/admin">Админ-панель</a>
      </div>

      <h2>Текущее задание</h2>
      {!task && <button onClick={loadToday}>Загрузить</button>}
      {task && (
        <div style={{ border: "1px solid #ddd", padding: 12 }}>
          <div>{task.text}</div>
          <div>Статус: {task.status}</div>
          {task.status !== "completed" && (
            <button onClick={() => complete(task.id)}>Выполнить</button>
          )}
        </div>
      )}

      <h2>Прогресс</h2>
      {progress ? (
        <div>
          <div>Всего: {progress.total}</div>
          <div>Выполнено: {progress.completed}</div>
          <div>Сегодня: {progress.today_completed}</div>
          <div>Неделя: {progress.week_completed}</div>
          <div>Месяц: {progress.month_completed}</div>
        </div>
      ) : (
        <div>Нет данных</div>
      )}
    </div>
  );
}
