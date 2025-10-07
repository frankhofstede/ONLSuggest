/**
 * Axios API client configured for ONLSuggest backend.
 * Base URL: http://localhost:8000 (FastAPI backend)
 * Includes request interceptor to inject Authorization header from localStorage.
 */
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Request interceptor: Inject Authorization header if token exists
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Handle common errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized: Clear token and redirect to login
      localStorage.removeItem('auth_token');
      // TODO: Add redirect logic when routing is set up
    }
    return Promise.reject(error);
  }
);

export default apiClient;
