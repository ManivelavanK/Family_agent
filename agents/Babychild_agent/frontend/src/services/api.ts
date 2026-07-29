import axios from 'axios';

// Always use mock mode for now — backend integration later
export const IS_MOCK_MODE = true;

// Use relative /api path so Vite's dev proxy routes requests to http://localhost:8000
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});
