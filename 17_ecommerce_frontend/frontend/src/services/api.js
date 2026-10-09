/**
 * Centralized Axios client instance for Day 13 E-Commerce Frontend.
 * Features:
 *  - Automated JWT Bearer token injection via Request Interceptor
 *  - 401 Session Expiration auto-logout and redirect via Response Interceptor
 *  - Real-time event broadcasting for live Interceptor Inspector monitoring
 *  - Friendly error normalization and structured diagnostics
 */
import axios from 'axios';
import { toast } from '../components/ui/sonner';

// Create base Axios instance
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Event bus / diagnostic store for interceptor activity monitoring
export const interceptorLogs = [];
const MAX_LOGS = 50;

function logInterceptorEvent(event) {
  interceptorLogs.unshift({
    id: Date.now() + Math.random(),
    timestamp: new Date().toLocaleTimeString(),
    ...event,
  });
  if (interceptorLogs.length > MAX_LOGS) {
    interceptorLogs.pop();
  }
  // Dispatch custom window event for reactive UI updates in Day13LabPage
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('axios:interceptor', { detail: event }));
  }
}

// -------------------------------------------------------------
// REQUEST INTERCEPTOR
// -------------------------------------------------------------
api.interceptors.request.use(
  (config) => {
    // Record start time for latency measurement
    config.metadata = { startTime: new Date() };

    // Read JWT access token from localStorage
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    logInterceptorEvent({
      type: 'REQUEST',
      method: (config.method || 'GET').toUpperCase(),
      url: config.url || '',
      hasToken: Boolean(token),
      tokenPreview: token ? `${token.substring(0, 10)}...${token.slice(-6)}` : null,
      headers: {
        'Content-Type': config.headers['Content-Type'],
        Authorization: token ? `Bearer ${token.substring(0, 10)}...` : 'None',
      },
    });

    return config;
  },
  (error) => {
    logInterceptorEvent({
      type: 'REQUEST_ERROR',
      error: error.message || 'Request creation failed',
    });
    return Promise.reject(error);
  }
);

// -------------------------------------------------------------
// RESPONSE INTERCEPTOR
// -------------------------------------------------------------
api.interceptors.response.use(
  (response) => {
    const startTime = response.config?.metadata?.startTime || new Date();
    const duration = new Date() - startTime;

    logInterceptorEvent({
      type: 'RESPONSE',
      status: response.status,
      statusText: response.statusText,
      url: response.config.url || '',
      duration: `${duration}ms`,
      dataPreview: Array.isArray(response.data)
        ? `Array(${response.data.length})`
        : typeof response.data === 'object' && response.data !== null
        ? response.data.items
          ? `List (items: ${response.data.items.length}, total: ${response.data.total})`
          : Object.keys(response.data).join(', ')
        : 'Text / Primitive',
    });

    return response;
  },
  (error) => {
    const status = error.response?.status;
    const url = error.config?.url || '';
    const detail =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred';

    logInterceptorEvent({
      type: 'RESPONSE_ERROR',
      status: status || 0,
      url: url,
      detail: typeof detail === 'string' ? detail : JSON.stringify(detail),
    });

    // 401 Unauthorized handling: Purge invalid credentials & redirect
    if (status === 401) {
      const hadToken = Boolean(localStorage.getItem('token'));
      localStorage.removeItem('token');
      localStorage.removeItem('user');

      // Notify user of expired session
      if (hadToken) {
        toast.error('Session Expired', {
          description: 'Your login session has expired or is invalid. Please sign in again.',
        });
      }

      // Avoid redirect loop if already navigating to login
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        const redirectPath = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/login?redirect=${redirectPath}`;
      }
    } else if (status === 403) {
      toast.error('Access Denied', {
        description: 'You do not have permissions to perform this operation.',
      });
    }

    return Promise.reject(error);
  }
);

export default api;
