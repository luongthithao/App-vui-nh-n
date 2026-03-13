const LOCAL_HOSTS = ["127.0.0.1", "localhost"];

const isLocal = LOCAL_HOSTS.includes(window.location.hostname);

export const API_BASE_URL = isLocal
  ? "http://127.0.0.1:8000"
  : "https://YOUR-RENDER-SERVICE.onrender.com";