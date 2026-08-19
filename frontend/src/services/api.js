import axios from 'axios';

/**
 * Standardized API Client for LocalSM Secure AI Exam Portal
 * Configured with environment-based base URL, request interceptors, and user-friendly error formatting.
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request Interceptor: Attach Bearer Token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('exam_portal_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Translate technical network/server errors into human-readable messages
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log developer-level error for diagnostics
    console.error('[API Diagnostic Error]', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    });

    let friendlyMessage = 'An unexpected error occurred. Please try again.';

    if (!error.response) {
      // Network failure / server offline
      friendlyMessage = 'Unable to connect to the server. Please check your internet connection and try again.';
    } else {
      const status = error.response.status;
      if (status === 400) {
        friendlyMessage = error.response.data?.message || 'Invalid request. Please check the entered details.';
      } else if (status === 401) {
        friendlyMessage = 'Session expired or unauthorized credentials. Please sign in again.';
        localStorage.removeItem('exam_portal_token');
      } else if (status === 403) {
        friendlyMessage = 'Access restricted. You do not have permission to view this resource.';
      } else if (status === 404) {
        friendlyMessage = 'The requested resource could not be found on the server.';
      } else if (status === 429) {
        friendlyMessage = 'Too many requests. Please wait a moment before trying again.';
      } else if (status >= 500) {
        friendlyMessage = 'The university exam server is temporarily unavailable. Please contact the technical administrator.';
      }
    }

    const enhancedError = new Error(friendlyMessage);
    enhancedError.originalError = error;
    enhancedError.statusCode = error.response?.status;
    enhancedError.isNetworkError = !error.response;

    return Promise.reject(enhancedError);
  }
);

export default api;
