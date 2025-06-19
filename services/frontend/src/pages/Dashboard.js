import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { 
  MessageCircle, 
  Send, 
  Plus, 
  LogOut, 
  User, 
  Trash2,
  Menu,
  X
} from 'lucide-react';
import toast from 'react-hot-toast';
import { chatAPI, sessionAPI, authAPI } from '../services/api';
import { UserUtils, AuthGuard } from '../utils/auth';

const DashboardContainer = styled.div`
  height: 100vh;
  display: flex;
  background: #f8fafc;
`;

const Sidebar = styled.div`
  width: 300px;
  background: white;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease;
  
  @media (max-width: 768px) {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transform: ${props => props.isOpen ? 'translateX(0)' : 'translateX(-100%)'};
  }
`;

const SidebarHeader = styled.div`
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
`;

const UserAvatar = styled.div`
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
`;

const UserName = styled.div`
  font-weight: 600;
  color: #1f2937;
`;

const NewChatButton = styled.button`
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-1px);
  }
`;

const SessionList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
`;

const SessionItem = styled.div`
  padding: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  margin-bottom: 0.5rem;
  background: ${props => props.active ? '#f1f5f9' : 'transparent'};
  border: ${props => props.active ? '1px solid #667eea' : '1px solid transparent'};
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  &:hover {
    background: #f8fafc;
  }
`;

const SessionTitle = styled.div`
  font-weight: 500;
  color: #374151;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const DeleteButton = styled.button`
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  opacity: 0;
  transition: all 0.2s;
  
  ${SessionItem}:hover & {
    opacity: 1;
  }
  
  &:hover {
    color: #ef4444;
    background: #fef2f2;
  }
`;

const SidebarFooter = styled.div`
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
`;

const LogoutButton = styled.button`
  width: 100%;
  background: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background 0.2s;
  
  &:hover {
    background: #e5e7eb;
  }
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
`;

const Header = styled.div`
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const MenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.25rem;
  
  &:hover {
    background: #f3f4f6;
  }
  
  @media (max-width: 768px) {
    display: block;
  }
`;

const ChatTitle = styled.h1`
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const ChatArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const MessageBubble = styled.div`
  max-width: 70%;
  padding: 1rem;
  border-radius: 1rem;
  align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  background: ${props => props.isUser 
    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
    : 'white'};
  color: ${props => props.isUser ? 'white' : '#374151'};
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: ${props => props.isUser ? 'none' : '1px solid #e2e8f0'};
  word-wrap: break-word;
`;

const EmptyState = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  text-align: center;
  gap: 1rem;
`;

const EmptyIcon = styled.div`
  width: 80px;
  height: 80px;
  background: #f3f4f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
`;

const ChatInput = styled.div`
  background: white;
  border-top: 1px solid #e2e8f0;
  padding: 1.5rem;
`;

const InputContainer = styled.div`
  display: flex;
  gap: 1rem;
  align-items: flex-end;
`;

const MessageInput = styled.textarea`
  flex: 1;
  border: 1px solid #d1d5db;
  border-radius: 0.75rem;
  padding: 1rem;
  font-size: 1rem;
  resize: none;
  min-height: 60px;
  max-height: 120px;
  transition: border-color 0.2s;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const SendButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 0.75rem;
  padding: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const Overlay = styled.div`
  display: ${props => props.show ? 'block' : 'none'};
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  
  @media (min-width: 769px) {
    display: none;
  }
`;

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const chatAreaRef = useRef(null);

  // 인증 확인 및 사용자 정보 로드
  useEffect(() => {
    if (!AuthGuard.requireAuth(navigate)) return;
    
    const userData = UserUtils.getUser();
    if (userData) {
      setUser(userData);
    } else {
      // 사용자 정보가 없으면 API에서 가져오기
      fetchCurrentUser();
    }
    
    fetchSessions();
  }, [navigate]);

  // 채팅 영역 스크롤 자동 이동
  useEffect(() => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const fetchCurrentUser = async () => {
    try {
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      UserUtils.setUser(userData);
    } catch (error) {
      toast.error('사용자 정보를 불러올 수 없습니다.');
      handleLogout();
    }
  };

  const fetchSessions = async () => {
    try {
      const sessionsData = await sessionAPI.getUserSessions();
      setSessions(sessionsData);
    } catch (error) {
      toast.error('세션 목록을 불러올 수 없습니다.');
    }
  };

  const createNewSession = async () => {
    try {
      const newSession = await sessionAPI.createSession();
      setSessions(prev => [newSession, ...prev]);
      setCurrentSession(newSession);
      setMessages([]);
      setSidebarOpen(false);
      toast.success('새로운 대화를 시작했습니다.');
    } catch (error) {
      toast.error('새 세션을 생성할 수 없습니다.');
    }
  };

  const selectSession = async (session) => {
    setCurrentSession(session);
    setSidebarOpen(false);
    
    try {
      const conversation = await chatAPI.getConversation(session.id);
      setMessages(conversation.messages || []);
    } catch (error) {
      toast.error('대화 내용을 불러올 수 없습니다.');
      setMessages([]);
    }
  };

  const deleteSession = async (sessionId, e) => {
    e.stopPropagation();
    
    try {
      await chatAPI.deleteConversation(sessionId);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        setMessages([]);
      }
      
      toast.success('대화가 삭제되었습니다.');
    } catch (error) {
      toast.error('대화를 삭제할 수 없습니다.');
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      content: inputMessage,
      is_user: true,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage(inputMessage, currentSession?.id);
      
      const botMessage = {
        content: response.response,
        is_user: false,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, botMessage]);
      
      // 새 세션이 생성된 경우 세션 목록 업데이트
      if (response.session_id && !currentSession) {
        fetchSessions();
      }
      
    } catch (error) {
      toast.error('메시지를 전송할 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleLogout = () => {
    authAPI.logout();
    UserUtils.removeUser();
    navigate('/login');
    toast.success('로그아웃되었습니다.');
  };

  return (
    <DashboardContainer>
      <Overlay show={sidebarOpen} onClick={() => setSidebarOpen(false)} />
      
      <Sidebar isOpen={sidebarOpen}>
        <SidebarHeader>
          <UserInfo>
            <UserAvatar>
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </UserAvatar>
            <UserName>{user?.username || '사용자'}</UserName>
          </UserInfo>
          <NewChatButton onClick={createNewSession}>
            <Plus size={20} />
            새로운 대화
          </NewChatButton>
        </SidebarHeader>
        
        <SessionList>
          {sessions.map(session => (
            <SessionItem
              key={session.id}
              active={currentSession?.id === session.id}
              onClick={() => selectSession(session)}
            >
              <SessionTitle>{session.title || '새로운 대화'}</SessionTitle>
              <DeleteButton onClick={(e) => deleteSession(session.id, e)}>
                <Trash2 size={16} />
              </DeleteButton>
            </SessionItem>
          ))}
        </SessionList>
        
        <SidebarFooter>
          <LogoutButton onClick={handleLogout}>
            <LogOut size={20} />
            로그아웃
          </LogoutButton>
        </SidebarFooter>
      </Sidebar>

      <MainContent>
        <Header>
          <MenuButton onClick={() => setSidebarOpen(true)}>
            <Menu size={24} />
          </MenuButton>
          <ChatTitle>
            <MessageCircle size={24} />
            {currentSession?.title || 'AI 챗봇'}
          </ChatTitle>
        </Header>

        <ChatArea ref={chatAreaRef}>
          {messages.length === 0 ? (
            <EmptyState>
              <EmptyIcon>
                <MessageCircle size={40} />
              </EmptyIcon>
              <div>
                <h3>새로운 대화를 시작해보세요!</h3>
                <p>아래 입력창에 메시지를 입력하면 AI가 답변해드립니다.</p>
              </div>
            </EmptyState>
          ) : (
            messages.map((message, index) => (
              <MessageBubble key={index} isUser={message.is_user}>
                {message.content}
              </MessageBubble>
            ))
          )}
        </ChatArea>

        <ChatInput>
          <InputContainer>
            <MessageInput
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="메시지를 입력하세요..."
              disabled={loading}
            />
            <SendButton onClick={sendMessage} disabled={loading || !inputMessage.trim()}>
              <Send size={20} />
            </SendButton>
          </InputContainer>
        </ChatInput>
      </MainContent>
    </DashboardContainer>
  );
};

export default Dashboard;
