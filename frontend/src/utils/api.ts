import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const apiClient = axios.create({
  baseURL: 'https://janjan-backend.vercel.app',
  withCredentials: true, // 세션 쿠키를 포함하여 요청 (회원가입 세션 유지용)
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터: 토큰 자동 주입
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터: 401 에러(토큰 만료) 처리
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      const authStore = useAuthStore();
      authStore.logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
