import axios from 'axios';

// nginx를 통해 프록시되는 경로로 변경
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost';

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 - 토큰 자동 추가
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 401 에러 시 로그아웃 처리
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 인증 API
export const authAPI = {
  // 회원가입
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  // 로그인
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
  },

  // 현재 사용자 정보
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // 로그아웃
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};

// 채팅 API
export const chatAPI = {
  // 채팅 메시지 전송
  sendMessage: async (message, sessionId = null) => {
    const response = await api.post('/chat', {
      message,
      session_id: sessionId
    });
    return response.data;
  },

  // 간단한 채팅 (인증 불필요)
  sendSimpleMessage: async (message) => {
    const response = await api.post('/simple-chat', { message });
    return response.data;
  },

  // 대화 내용 조회
  getConversation: async (sessionId) => {
    const response = await api.get(`/conversation/${sessionId}`);
    return response.data;
  },

  // 대화 삭제
  deleteConversation: async (sessionId) => {
    const response = await api.delete(`/conversation/${sessionId}`);
    return response.data;
  }
};

// 세션 API
export const sessionAPI = {
  // 새 세션 생성
  createSession: async (title = '새로운 대화') => {
    const response = await api.post('/sessions', { title });
    return response.data;
  },

  // 사용자 세션 목록 조회
  getUserSessions: async () => {
    const response = await api.get('/sessions');
    return response.data;
  }
};

// 헬스 체크 API
export const healthAPI = {
  checkHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  }
};

export default api; 