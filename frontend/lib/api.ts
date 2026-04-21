import axios from 'axios';

const rawBaseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
// Ensure no trailing slash for consistency
const cleanBaseURL = rawBaseURL.endsWith('/') ? rawBaseURL.slice(0, -1) : rawBaseURL;

const api = axios.create({
  baseURL: cleanBaseURL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
