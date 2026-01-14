/**
 * Axios API Service
 * ================
 * Centralized HTTP client with interceptors for authentication and error handling.
 * 
 * Features:
 * - Request interceptor: Add auth tokens (future Keycloak)
 * - Response interceptor: Handle errors globally
 * - Base URL configuration
 */

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { message } from 'antd';
import { API_CONFIG } from '../config/api.config';

/**
 * Create Axios instance with base configuration
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request Interceptor
 * 
 * Adds authentication token to requests (future Keycloak integration).
 * Currently no auth, but structure is ready.
 */
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    /**
     * Attach Keycloak access token when present.
     * Token is expected to be stored by the auth flow in localStorage.
     */
    const token =
      localStorage.getItem('keycloak_token') ||
      localStorage.getItem('access_token') ||
      sessionStorage.getItem('keycloak_token');

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor
 * 
 * Handles common error scenarios:
 * - 401 Unauthorized: Redirect to login (future)
 * - 403 Forbidden: Show permission error
 * - 404 Not Found: Show not found error
 * - 500 Server Error: Show server error
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle error responses
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as any;

      switch (status) {
        case 401:
          // Unauthorized - redirect to login (future)
          message.error('Session expired. Please login again.');
          // window.location.href = '/login';
          break;

        case 403:
          message.error('You do not have permission to perform this action.');
          break;

        case 404:
          message.error(data?.detail || 'Resource not found.');
          break;

        case 409:
          // Conflict - usually duplicate entry
          message.error(data?.detail || 'A conflict occurred. The resource may already exist.');
          break;

        case 422:
          // Validation error
          message.error(data?.detail || 'Validation error. Please check your input.');
          break;

        case 500:
          message.error('Server error. Please try again later.');
          break;

        default:
          message.error(data?.detail || 'An unexpected error occurred.');
      }
    } else if (error.request) {
      // Request made but no response received
      message.error('No response from server. Please check your connection.');
    } else {
      // Something else happened
      message.error('An error occurred while processing your request.');
    }

    return Promise.reject(error);
  }
);

export default apiClient;


