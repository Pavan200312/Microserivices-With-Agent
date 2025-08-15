import axios from 'axios';

// API base URL - use localhost for development, Docker service name for production
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API service functions
export const apiService = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Start tracking
  startTracking: async () => {
    const response = await api.post('/api/tracking/start');
    return response.data;
  },

  // Get commits
  getCommits: async () => {
    const response = await api.get('/api/commits');
    return response.data;
  },

  // Get specific commit
  getCommit: async (commitHash) => {
    const response = await api.get(`/api/commits/${commitHash}`);
    return response.data;
  },

  // Get AI analysis for commit
  getAnalysis: async (commitHash) => {
    const response = await api.get(`/api/analysis/${commitHash}`);
    return response.data;
  },

  // Fetch new commits (trigger manual fetch)
  fetchCommits: async () => {
    const response = await api.post('/api/fetch-commits');
    return response.data;
  },
};

// Error handling utility
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    switch (status) {
      case 404:
        return 'Resource not found';
      case 500:
        return 'Server error occurred';
      default:
        return data?.detail || `Error ${status}: ${data?.message || 'Unknown error'}`;
    }
  } else if (error.request) {
    // Network error
    return 'Network error: Unable to connect to server';
  } else {
    // Other error
    return error.message || 'An unexpected error occurred';
  }
};

export default api;
