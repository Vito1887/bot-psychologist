import { useEffect, useState } from "react";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Admin() {
  const [token, setToken] = useState<string | null>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [exercises, setExercises] = useState<string[]>([]);
  const [newExercise, setNewExercise] = useState("");
  const [msg, setMsg] = useState("");

  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    const t = localStorage.getItem("token");
    if (t) setToken(t);
  }, []);

  const loadUsers = async () => {
    try {
      const { data } = await axios.get(`${API_URL}/api/admin/users`, {
        withCredentials: true,
        headers: authHeaders,
      });
      setUsers(data);
    } catch (e: any) {
      setMsg("Ошибка загрузки пользователей");
    }
  };

  const loadExercises = async () => {
    try {
      const { data } = await axios.get(`${API_URL}/api/admin/exercises`, {
        withCredentials: true,
        headers: authHeaders,
      });
      setExercises(data);
    } catch (e: any) {
      setMsg("Ошибка загрузки упражнений");
    }
  };

  const addExercise = async () => {
    try {
      const { data } = await axios.post(
        `${API_URL}/api/admin/exercises`,
        null,
        {
          params: { text: newExercise },
          withCredentials: true,
          headers: authHeaders,
        }
      );
      setExercises(data);
      setNewExercise("");
    } catch (e: any) {
      setMsg("Ошибка добавления упражнения");
    }
  };

  const removeExercise = async (index: number) => {
    try {
      const { data } = await axios.delete(
        `${API_URL}/api/admin/exercises/${index}`,
        {
          withCredentials: true,
          headers: authHeaders,
        }
      );
      setExercises(data);
    } catch (e: any) {
      setMsg("Ошибка удаления упражнения");
    }
  };

  const loadTasksForUser = async (userId: number) => {
    try {
      const { data } = await axios.get(
        `${API_URL}/api/admin/users/${userId}/tasks`,
        {
          withCredentials: true,
          headers: authHeaders,
        }
      );
      setTasks(data);
    } catch (e: any) {
      setMsg("Ошибка загрузки задач пользователя");
    }
  };

  const generateToday = async (userId: number) => {
    try {
      await axios.post(`${API_URL}/api/admin/generate_today/${userId}`, null, {
        withCredentials: true,
        headers: authHeaders,
      });
      await loadTasksForUser(userId);
    } catch (e: any) {
      setMsg("Ошибка генерации");
    }
  };

  useEffect(() => {
    if (!token) return;
    loadUsers();
    loadExercises();
  }, [token]);

  return (
    <div style={{ padding: 24, fontFamily: "sans-serif", maxWidth: 1000 }}>
      <h1>Админ-панель</h1>
      <p>{msg}</p>

      <h2>Упражнения</h2>
      <div style={{ display: "flex", gap: 8 }}>
        <input
          placeholder="Новое упражнение"
          value={newExercise}
          onChange={(e) => setNewExercise(e.target.value)}
        />
        <button onClick={addExercise}>Добавить</button>
      </div>
      <ol>
        {exercises.map((e, i) => (
          <li key={i}>
            {e} <button onClick={() => removeExercise(i)}>Удалить</button>
          </li>
        ))}
      </ol>

      <h2>Пользователи</h2>
      <div>
        {users.map((u) => (
          <div
            key={u.id}
            style={{ borderBottom: "1px solid #eee", padding: 8 }}
          >
            <div>
              {u.name} ({u.email}) — роль: {u.role}
              <button
                style={{ marginLeft: 8 }}
                onClick={() => {
                  setSelectedUserId(u.id);
                  loadTasksForUser(u.id);
                }}
              >
                Задачи
              </button>
              <button
                style={{ marginLeft: 8 }}
                onClick={() => generateToday(u.id)}
              >
                Создать задание на сегодня
              </button>
            </div>
          </div>
        ))}
      </div>

      {selectedUserId && (
        <div>
          <h3>Задачи пользователя #{selectedUserId}</h3>
          {tasks.map((t) => (
            <div
              key={t.id}
              style={{ borderBottom: "1px solid #eee", padding: 8 }}
            >
              <div>{new Date(t.sent_at).toLocaleString()}</div>
              <div>{t.text}</div>
              <div>Статус: {t.status}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
