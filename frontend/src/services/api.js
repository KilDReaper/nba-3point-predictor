import axios from "axios";

const getBaseURL = () => {
  // If running in development (e.g. standard Vite dev server on 5173 or other local hosts), map to FastAPI port 8000
  if (window.location.hostname === "localhost" && window.location.port !== "3000") {
    return "http://localhost:8000";
  }
  // If running via docker-compose on port 3000, Nginx proxies /api to backend:8000
  if (window.location.port === "3000") {
    return "/api";
  }
  // Fallback to local API port
  return "http://localhost:8000";
};

const api = axios.create({
  baseURL: getBaseURL(),
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;