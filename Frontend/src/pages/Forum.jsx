import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL, WS_URL } from '../config';
import '../App.css';

const VALID_NAME_REGEX = /^[a-zA-Z0-9-_]+$/;

function Forum() {
  const [authState, setAuthState] = useState('loading');
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  const messagesEndRef = useRef(null); 
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  
  const [chats, setChats] = useState([]); 
  const [selectedChat, setSelectedChat] = useState('main');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newChatName, setNewChatName] = useState('');
  const [modalError, setModalError] = useState('');

  const [isChatReady, setIsChatReady] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 1. Auth check
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      setAuthState('unauthenticated');
      return;
    }

    const fetchUser = async () => {
      try {
        const response = await fetch(`${API_URL}/api/users/me`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (response.status === 401) {
          localStorage.removeItem('token');
          setAuthState('unauthenticated');
          return;
        }
        const userData = await response.json();
        setUser(userData);
        setAuthState(userData.is_active ? 'active' : 'locked');
      } catch (error) {
        setAuthState('unauthenticated');
      }
    };
    fetchUser();
  }, []);

  // 2. Polling for chat list
  const fetchChats = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    try {
      const response = await fetch(`${API_URL}/api/chat/list`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        const cleanChats = data.map(name => name.replace('chat_', ''));
        setChats(cleanChats);
      }
    } catch (error) {
      console.error("Fetch error:", error);
    }
  }, []);

  useEffect(() => {
    if (authState === 'active') {
      fetchChats();
      const interval = setInterval(fetchChats, 5000); 
      return () => clearInterval(interval);
    }
  }, [authState, fetchChats]);

  // 3. Create Chat logic 
  const handleCreateChat = async () => {
    setModalError('');
    const chatName = newChatName.trim();
    if (!chatName) return;

    if (!VALID_NAME_REGEX.test(chatName)) {
      setModalError('Nazwa może zawierać tylko litery, cyfry, "-" i "_" (bez spacji).');
      return;
    }

    setIsCreating(true);
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`${API_URL}/api/chat/create/${chatName}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        setNewChatName('');
        setIsModalOpen(false);
        await fetchChats();
      } else {
        const errorData = await response.json();
        setModalError(errorData.detail || 'Błąd tworzenia czatu.');
      }
    } catch (error) {
      setModalError('Błąd połączenia.');
    } finally {
      setIsCreating(false);
    }
  };

  // 4. Chat Status Polling - Checks if selectedChat is ACTIVE before connecting WS
  useEffect(() => {
    if (authState !== 'active' || !selectedChat) return;

    setIsChatReady(false);
    let isMounted = true;
    const token = localStorage.getItem('token');

    const checkStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/api/chat/status/${selectedChat}`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        const data = await response.json();
        
        if (isMounted && data.status === 'ACTIVE') {
          setIsChatReady(true);
        } else if (isMounted) {
          setTimeout(checkStatus, 1000);
        }
      } catch (error) {
        console.error("Status check error:", error);
      }
    };

    checkStatus();
    return () => { isMounted = false; };
  }, [selectedChat, authState]);

  // 5. WebSocket - Only connects if isChatReady is true
  useEffect(() => {
    if (authState !== 'active' || !user || !isChatReady) return;

    if (!VALID_NAME_REGEX.test(selectedChat)) {
        console.error("Invalid chat name for WS:", selectedChat);
        return;
    }

    setMessages([]); 
    let isMounted = true;
    const token = localStorage.getItem('token');
    const ws = new WebSocket(`${WS_URL}/api/ws/chat/${selectedChat}`);
    
    ws.onopen = () => {
      if (isMounted) {
        setSocket(ws);
        ws.send(token); 
      }
    };

    ws.onmessage = (event) => {
      if (!isMounted) return;
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'history') {
          setMessages(data.messages.map((msg, idx) => ({
            id: `h-${idx}-${Date.now()}`, 
            content: msg.message,
            username: msg.username,
            timestamp: msg.timestamp,
            isOwn: msg.username === user.username
          })));
        } 
        else if (data.type === 'message') {
          setMessages(prev => [...prev, {
            id: Date.now(),
            content: data.message,
            username: data.username,
            timestamp: data.timestamp,
            isOwn: data.username === user.username
          }]);
        }
      } catch (e) {
        console.error("WS parse error:", e);
      }
    };

    return () => {
      isMounted = false;
      ws.close();
      setSocket(null);
    };
  }, [authState, user, selectedChat, isChatReady]);

  const sendMessage = useCallback(() => {
    if (newMessage.trim() && socket && socket.readyState === WebSocket.OPEN) {
      socket.send(newMessage.trim()); 
      setNewMessage('');
    }
  }, [socket, newMessage]);

  const closeModal = () => {
    setIsModalOpen(false);
    setModalError('');
    setNewChatName('');
  };

  // --- RENDER ---
  if (authState === 'loading') return <div className="forum-container"><h2>Ładowanie...</h2></div>;
  if (authState === 'unauthenticated') return (
    <div className="forum-container"><div className="no-thread-selected"><button onClick={() => navigate('/login')}>Zaloguj się</button></div></div>
  );

  return (
    <div className="forum-container">
      <aside className="thread-list">
        <div className="thread-header">
          <h2 className="brand-logo">ryBMW</h2>
          <button className="new-thread-btn-text" onClick={() => setIsModalOpen(true)}>Nowy czat</button>
        </div>
        <div className="threads">
          {chats.map((chat) => (
            <div 
              key={chat} 
              className={`thread-item ${selectedChat === chat ? 'selected' : ''}`}
              onClick={() => setSelectedChat(chat)}
            >
              <h3>#{chat}</h3>
            </div>
          ))}
        </div>
      </aside>

      <main className="chat-area">
        <div className="thread-title">Czat: {selectedChat}</div>
        <div className="messages">
          {!isChatReady ? (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Inicjalizacja czatu...</p>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <div key={msg.id} className={`message ${msg.isOwn ? "own" : ""}`}> 
                  <div className="message-header">
                    <span className="username">{msg.username}</span>
                    <span className="timestamp">{new Date(msg.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <p>{msg.content}</p>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
        
        <div className="message-input">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder={socket ? "Napisz wiadomość..." : "Łączenie..."}
            disabled={!socket || !isChatReady}
          />
          <button onClick={sendMessage} disabled={!socket || !isChatReady}>Wyślij</button>
        </div>
      </main>

      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Utwórz nowy czat</h3>
            {isCreating ? (
              <div className="loading-container">
                <div className="spinner"></div>
                <p>Tworzenie tabeli...</p>
              </div>
            ) : (
              <>
                {modalError && <div className="error-message" style={{color: 'red', marginBottom: '10px'}}>{modalError}</div>}
                <input 
                  type="text" 
                  placeholder="Nazwa czatu..." 
                  value={newChatName}
                  onChange={(e) => setNewChatName(e.target.value)}
                />
                <div className="modal-buttons">
                  <button onClick={handleCreateChat}>Utwórz</button>
                  <button onClick={closeModal}>Anuluj</button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Forum;
