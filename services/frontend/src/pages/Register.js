import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { UserPlus, Eye, EyeOff, Mail, User } from 'lucide-react';
import toast from 'react-hot-toast';
import { authAPI } from '../services/api';
import { UserUtils, AuthGuard, ValidationUtils, ErrorUtils } from '../utils/auth';

const RegisterContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
`;

const RegisterCard = styled.div`
  background: white;
  border-radius: 1rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  padding: 2rem;
  width: 100%;
  max-width: 400px;
`;

const Title = styled.h1`
  text-align: center;
  font-size: 2rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
`;

const Subtitle = styled.p`
  text-align: center;
  color: #6b7280;
  margin-bottom: 2rem;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
`;

const Label = styled.label`
  font-weight: 500;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const InputWrapper = styled.div`
  position: relative;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  &.error {
    border-color: #ef4444;
  }

  &.success {
    border-color: #10b981;
  }
`;

const PasswordToggle = styled.button`
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  
  &:hover {
    color: #374151;
  }
`;

const ErrorMessage = styled.span`
  color: #ef4444;
  font-size: 0.875rem;
`;

const SuccessMessage = styled.span`
  color: #10b981;
  font-size: 0.875rem;
`;

const PasswordHint = styled.div`
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
`;

const RegisterButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s;
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const LoginLink = styled.div`
  text-align: center;
  margin-top: 1.5rem;
  color: #6b7280;
  
  a {
    color: #667eea;
    text-decoration: none;
    font-weight: 500;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  // 이미 로그인된 사용자는 대시보드로 리다이렉트
  useEffect(() => {
    AuthGuard.requireGuest(navigate);
  }, [navigate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // 입력 시 에러 메시지 제거
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateField = (name, value) => {
    switch (name) {
      case 'username':
        return ErrorUtils.getValidationError('username', value);
      case 'email':
        return ErrorUtils.getValidationError('email', value);
      case 'password':
        return ErrorUtils.getValidationError('password', value);
      case 'confirmPassword':
        if (!value) return '비밀번호 확인을 입력해주세요.';
        if (value !== formData.password) return '비밀번호가 일치하지 않습니다.';
        return null;
      default:
        return null;
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    Object.keys(formData).forEach(field => {
      const error = validateField(field, formData[field]);
      if (error) {
        newErrors[field] = error;
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await authAPI.register({
        username: formData.username,
        email: formData.email,
        password: formData.password
      });
      
      toast.success('회원가입이 완료되었습니다! 로그인해주세요.');
      navigate('/login');
      
    } catch (error) {
      const errorMessage = ErrorUtils.parseError(error);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getInputClassName = (fieldName) => {
    if (errors[fieldName]) return 'error';
    if (formData[fieldName] && !errors[fieldName] && formData[fieldName].length > 0) {
      const error = validateField(fieldName, formData[fieldName]);
      return error ? 'error' : 'success';
    }
    return '';
  };

  return (
    <RegisterContainer>
      <RegisterCard>
        <Title>
          <UserPlus size={24} />
          회원가입
        </Title>
        <Subtitle>새로운 계정을 만들어 AI 챗봇을 이용해보세요</Subtitle>
        
        <Form onSubmit={handleSubmit}>
          <InputGroup>
            <Label htmlFor="username">
              <User size={16} />
              사용자명
            </Label>
            <Input
              id="username"
              name="username"
              type="text"
              value={formData.username}
              onChange={handleInputChange}
              className={getInputClassName('username')}
              placeholder="사용자명을 입력하세요 (3-20자)"
            />
            {errors.username && <ErrorMessage>{errors.username}</ErrorMessage>}
            {formData.username && !errors.username && ValidationUtils.isValidUsername(formData.username) && (
              <SuccessMessage>사용 가능한 사용자명입니다</SuccessMessage>
            )}
          </InputGroup>
          
          <InputGroup>
            <Label htmlFor="email">
              <Mail size={16} />
              이메일
            </Label>
            <Input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              className={getInputClassName('email')}
              placeholder="이메일을 입력하세요"
            />
            {errors.email && <ErrorMessage>{errors.email}</ErrorMessage>}
            {formData.email && !errors.email && ValidationUtils.isValidEmail(formData.email) && (
              <SuccessMessage>올바른 이메일 형식입니다</SuccessMessage>
            )}
          </InputGroup>
          
          <InputGroup>
            <Label htmlFor="password">비밀번호</Label>
            <InputWrapper>
              <Input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleInputChange}
                className={getInputClassName('password')}
                placeholder="비밀번호를 입력하세요"
              />
              <PasswordToggle
                type="button"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </PasswordToggle>
            </InputWrapper>
            {errors.password && <ErrorMessage>{errors.password}</ErrorMessage>}
            {formData.password && !errors.password && ValidationUtils.isValidPassword(formData.password) && (
              <SuccessMessage>안전한 비밀번호입니다</SuccessMessage>
            )}
            <PasswordHint>8자 이상, 대소문자 및 숫자 포함</PasswordHint>
          </InputGroup>
          
          <InputGroup>
            <Label htmlFor="confirmPassword">비밀번호 확인</Label>
            <InputWrapper>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className={getInputClassName('confirmPassword')}
                placeholder="비밀번호를 다시 입력하세요"
              />
              <PasswordToggle
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </PasswordToggle>
            </InputWrapper>
            {errors.confirmPassword && <ErrorMessage>{errors.confirmPassword}</ErrorMessage>}
            {formData.confirmPassword && !errors.confirmPassword && formData.confirmPassword === formData.password && (
              <SuccessMessage>비밀번호가 일치합니다</SuccessMessage>
            )}
          </InputGroup>
          
          <RegisterButton type="submit" disabled={loading}>
            {loading ? '가입 중...' : '회원가입'}
          </RegisterButton>
        </Form>
        
        <LoginLink>
          이미 계정이 있으신가요? <Link to="/login">로그인</Link>
        </LoginLink>
      </RegisterCard>
    </RegisterContainer>
  );
};

export default Register; 