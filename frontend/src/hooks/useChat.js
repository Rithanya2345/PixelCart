import { useState, useCallback, useRef } from "react";
import { sendChat, clearSession } from "../utils/api";

function genSessionId() {
  return "px_" + Math.random().toString(36).slice(2, 11);
}

export function useChat() {
  const [messages, setMessages]     = useState([]);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState(null);
  const sessionId = useRef(genSessionId());

  const addMessage = (msg) =>
    setMessages((prev) => [...prev, { id: Date.now() + Math.random(), ...msg }]);

  const send = useCallback(async (text) => {
    if (!text.trim() || loading) return;
    setError(null);
    addMessage({ type: "user", text });
    setLoading(true);
    const t0 = Date.now();
    try {
      const data = await sendChat(sessionId.current, text);
      addMessage({
        type:         "agent",
        text:         data.message,
        products:     data.products || [],
        followup:     data.followup || null,
        intent:       data.intent   || null,
        responseTime: Date.now() - t0,
      });
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.message ||
        "Something went wrong. Check that the backend is running.";
      setError(msg);
      addMessage({ type: "error", text: msg });
    } finally {
      setLoading(false);
    }
  }, [loading]);

  const reset = useCallback(async () => {
    try { await clearSession(sessionId.current); } catch (_) {}
    sessionId.current = genSessionId();
    setMessages([]);
    setError(null);
    setLoading(false);
  }, []);

  return { messages, loading, error, send, reset, sessionId: sessionId.current };
}
