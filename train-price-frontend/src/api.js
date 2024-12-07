import axios from 'axios';

// Create an axios instance with base configuration
const api = axios.create({
  baseURL: 'https://cd-price-tracker.onrender.com', // Make sure this matches your backend URL
  timeout: 10000, // 10 second timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('Request config:', config);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    console.log('Response:', response);
    return response;
  },
  (error) => {
    console.error('Full error details:', {
      message: error.message,
      code: error.code,
      response: error.response,
      request: error.request
    });
    return Promise.reject(error);
  }
);

export default api;