import axios from 'axios';

// Set this to false to connect to a real backend API (or toggle via settings UI)
export const IS_MOCK_MODE = localStorage.getItem('kinnest_mock_mode') === 'true';

// Use relative /api path so Vite's dev proxy routes requests to http://localhost:8000
// This avoids CORS completely. In production, ensure backend is reachable at /api/v1.
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});
