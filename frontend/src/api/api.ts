import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Automatic JWT injection interceptor
api.interceptors.request.use(
  (config) => {
    // Pull token directly from localStorage managed by useAuthStore
    const authState = localStorage.getItem('kinnest-auth-storage');
    if (authState) {
      try {
        const parsed = JSON.parse(authState);
        const token = parsed?.state?.token;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (err) {
        console.error('Interceptor failed to parse token:', err);
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// General response interceptor for unified error mapping
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const errorDetails = error.response?.data?.detail || error.response?.data?.error || error.message;
    console.error(`API Error: ${errorDetails}`);
    return Promise.reject(new Error(errorDetails));
  }
);
