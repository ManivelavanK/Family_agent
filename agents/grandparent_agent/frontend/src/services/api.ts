import axios from 'axios';
import { API_BASE_URL } from '../config/api';
import toast from 'react-hot-toast';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 5000, // 5 seconds timeout
});

// Helper to determine if the backend is offline/unavailable
export const isBackendUnavailable = (error: any): boolean => {
  return (
    !error.response || // No response received (network error)
    error.code === 'ECONNREFUSED' ||
    error.code === 'ERR_NETWORK' ||
    error.message?.includes('Network Error') ||
    error.message?.includes('timeout')
  );
};

// Response interceptor to handle unwrapping and error logging/toasting
api.interceptors.response.use(
  (response) => {
    // Check if it's the standard APIResponse wrapper
    if (response.data && typeof response.data === 'object' && 'success' in response.data) {
      if (response.data.success === false) {
        const error = new Error(response.data.message || 'API operation unsuccessful') as any;
        error.response = response;
        return Promise.reject(error);
      }
      // Unwrap backend APIResponse wrapper so response.data becomes the actual data payload
      response.data = response.data.data;
    }
    return response;
  },
  (error) => {
    // Log required error details
    console.error('--- API Error Details ---');
    console.error('Request URL:', error.config?.url);
    console.error('HTTP Method:', error.config?.method?.toUpperCase());
    console.error('Status Code:', error.response?.status ?? 'N/A (No Response)');
    console.error('Backend Error:', error.response?.data ?? error.message);
    console.error('------------------------');

    if (isBackendUnavailable(error)) {
      toast.error('Unable to connect to Grandparent Agent backend.');
    }

    return Promise.reject(error);
  }
);
