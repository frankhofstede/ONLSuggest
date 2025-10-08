// Admin API utility functions

export const API_URL = import.meta.env.VITE_API_URL || '';
const ADMIN_USERNAME = import.meta.env.VITE_ADMIN_USERNAME || 'admin';
const ADMIN_PASSWORD = import.meta.env.VITE_ADMIN_PASSWORD || 'admin123';

export const getAuthHeader = () => {
  const auth = btoa(`${ADMIN_USERNAME}:${ADMIN_PASSWORD}`);
  return `Basic ${auth}`;
};

export const adminFetch = async (endpoint: string, options: RequestInit = {}) => {
  const headers = {
    'Authorization': getAuthHeader(),
    ...options.headers
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
};
