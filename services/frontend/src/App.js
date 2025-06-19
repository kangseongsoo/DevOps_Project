import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import { UserUtils } from './utils/auth';

// 로그인 상태를 확인하는 컴포넌트
const ProtectedRoute = ({ children }) => {
  const isLoggedIn = UserUtils.isLoggedIn();
  console.log('ProtectedRoute - 로그인 상태:', isLoggedIn);
  console.log('ProtectedRoute - 토큰:', localStorage.getItem('token') ? '있음' : '없음');
  console.log('ProtectedRoute - 사용자:', UserUtils.getUser());
  
  return isLoggedIn ? children : <Navigate to="/login" replace />;
};

// 게스트 전용 라우트 (로그인된 사용자는 대시보드로)
const GuestRoute = ({ children }) => {
  const isLoggedIn = UserUtils.isLoggedIn();
  console.log('GuestRoute - 로그인 상태:', isLoggedIn);
  
  return isLoggedIn ? <Navigate to="/dashboard" replace /> : children;
};

const App = () => {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route 
            path="/" 
            element={
              UserUtils.isLoggedIn() ? 
                <Navigate to="/dashboard" replace /> : 
                <Navigate to="/login" replace />
            } 
          />
          <Route 
            path="/login" 
            element={
              <GuestRoute>
                <Login />
              </GuestRoute>
            } 
          />
          <Route 
            path="/register" 
            element={
              <GuestRoute>
                <Register />
              </GuestRoute>
            } 
          />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#4ade80',
                secondary: '#fff',
              },
            },
            error: {
              duration: 4000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </div>
    </Router>
  );
};

export default App; 