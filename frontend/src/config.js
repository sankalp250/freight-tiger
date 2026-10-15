// In development, default to local FastAPI backend.
// In production (Vercel), point to the deployed Render backend URL.
export const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
