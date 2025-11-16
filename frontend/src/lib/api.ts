import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001",
  headers: { "Content-Type": "application/json" },
});

export default api;