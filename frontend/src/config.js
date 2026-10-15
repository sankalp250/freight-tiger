// In development, default to local FastAPI backend.
// In production (Vercel/Render), automatically route to the live Render backend.
export const API_BASE = 
  import.meta.env.VITE_API_URL || 
  (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000'
    : 'https://freight-tiger-backend.onrender.com');
