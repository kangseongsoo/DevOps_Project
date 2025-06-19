// 토큰 관련 유틸리티
export const TokenUtils = {
  // 토큰 저장
  setToken: (token) => {
    localStorage.setItem('token', token);
  },

  // 토큰 가져오기
  getToken: () => {
    return localStorage.getItem('token');
  },

  // 토큰 삭제
  removeToken: () => {
    localStorage.removeItem('token');
  },

  // 토큰 유효성 검사
  isTokenValid: () => {
    const token = localStorage.getItem('token');
    console.log('토큰 유효성 검사 - 토큰:', token ? '있음' : '없음');
    
    if (!token) return false;

    try {
      // JWT 토큰 디코딩
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      
      console.log('토큰 페이로드:', payload);
      console.log('현재 시간:', currentTime);
      console.log('토큰 만료 시간:', payload.exp);
      console.log('토큰 유효:', payload.exp > currentTime);
      
      // 토큰 만료 시간 확인
      return payload.exp > currentTime;
    } catch (error) {
      console.error('토큰 디코딩 오류:', error);
      return false;
    }
  }
};

// 사용자 정보 관련 유틸리티
export const UserUtils = {
  // 사용자 정보 저장
  setUser: (user) => {
    localStorage.setItem('user', JSON.stringify(user));
  },

  // 사용자 정보 가져오기
  getUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  // 사용자 정보 삭제
  removeUser: () => {
    localStorage.removeItem('user');
  },

  // 로그인 상태 확인
  isLoggedIn: () => {
    const tokenValid = TokenUtils.isTokenValid();
    const user = UserUtils.getUser();
    const hasUser = user !== null;
    
    console.log('로그인 상태 확인:');
    console.log('- 토큰 유효:', tokenValid);
    console.log('- 사용자 정보:', hasUser ? '있음' : '없음');
    console.log('- 최종 로그인 상태:', tokenValid && hasUser);
    
    return tokenValid && hasUser;
  }
};

// 인증 보호 컴포넌트를 위한 유틸리티
export const AuthGuard = {
  // 로그인 필요한 페이지 접근 시 체크
  requireAuth: (navigate) => {
    if (!UserUtils.isLoggedIn()) {
      navigate('/login');
      return false;
    }
    return true;
  },

  // 이미 로그인된 사용자가 로그인/회원가입 페이지 접근 시 체크
  requireGuest: (navigate) => {
    if (UserUtils.isLoggedIn()) {
      navigate('/dashboard');
      return false;
    }
    return true;
  }
};

// 폼 유효성 검사 유틸리티
export const ValidationUtils = {
  // 이메일 유효성 검사
  isValidEmail: (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  // 비밀번호 유효성 검사 (최소 8자, 대소문자, 숫자 포함)
  isValidPassword: (password) => {
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password);
  },

  // 사용자명 유효성 검사 (3-20자, 영문, 숫자, 언더스코어만 허용)
  isValidUsername: (username) => {
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
    return usernameRegex.test(username);
  }
};

// 에러 메시지 유틸리티
export const ErrorUtils = {
  // API 에러 메시지 파싱
  parseError: (error) => {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message) {
      return error.message;
    }
    return '알 수 없는 오류가 발생했습니다.';
  },

  // 유효성 검사 에러 메시지
  getValidationError: (field, value) => {
    switch (field) {
      case 'email':
        if (!value) return '이메일을 입력해주세요.';
        if (!ValidationUtils.isValidEmail(value)) return '올바른 이메일 형식이 아닙니다.';
        break;
      case 'password':
        if (!value) return '비밀번호를 입력해주세요.';
        if (!ValidationUtils.isValidPassword(value)) {
          return '비밀번호는 8자 이상이며 대소문자와 숫자를 포함해야 합니다.';
        }
        break;
      case 'username':
        if (!value) return '사용자명을 입력해주세요.';
        if (!ValidationUtils.isValidUsername(value)) {
          return '사용자명은 3-20자의 영문, 숫자, 언더스코어만 허용됩니다.';
        }
        break;
      default:
        return null;
    }
    return null;
  }
}; 