import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
  timeout: 60000,
});

export async function sendChat(sessionId, message) {
  const { data } = await api.post("/api/chat", {
    session_id: sessionId,
    message,
  });
  return data;
}

export async function connectShopify(shopifyUrl, storefrontToken) {
  const { data } = await api.post("/api/connect-shopify", {
    shopify_url: shopifyUrl,
    storefront_token: storefrontToken,
  });
  return data;
}

export async function clearSession(sessionId) {
  const { data } = await api.delete(`/api/session/${sessionId}`);
  return data;
}

export async function checkHealth() {
  const { data } = await api.get("/api/health");
  return data;
}

export default api;
