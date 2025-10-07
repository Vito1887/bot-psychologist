import { useEffect, useState } from "react";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function History() {
  const [token, setToken] = useState<string | null>(null);
  const [items, setItems] = useState<any[]>([]);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    const t = localStorage.getItem("token");
    if (t) setToken(t);
  }, []);

  useEffect(() => {
    if (!token) return;
    axios
      .get(`${API_URL}/api/tasks`, {
        withCredentials: true,
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })
      .then((r) => setItems(r.data))
      .catch(() => setMsg("Ошибка загрузки"));
  }, [token]);

  return (
    <div style={{ padding: 24, fontFamily: "sans-serif", maxWidth: 800 }}>
      <h1>История заданий</h1>
      <p>{msg}</p>
      {!items.length && <div>Нет данных</div>}
      {items.map((t) => (
        <div key={t.id} style={{ borderBottom: "1px solid #eee", padding: 8 }}>
          <div>{new Date(t.sent_at).toLocaleString()}</div>
          <div>{t.text}</div>
          <div>Статус: {t.status}</div>
        </div>
      ))}
    </div>
  );
}
