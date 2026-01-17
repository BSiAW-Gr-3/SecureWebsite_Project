import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL, WS_URL } from '../config';
import '../App.css';

function Forum() {
  // --- STATE AND HOOKS ---
  const [authState, setAuthState] = useState('loading');
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  const messagesEndRef = useRef(null); 
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  
  // Dynamic Chat State
  const [chats, setChats] = useState([]); 
  const [selectedChat, setSelectedChat] = useState('main');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newChatName, setNewChatName] = useState('');

  // Auto-scroll do ostatniej wiadomości
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 1. Autentykacja użytkownika
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

  // 2. Pobieranie listy czatów (zdefiniowane jako useCallback dla pollingu)
  const fetchChats = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      const response = await fetch(`${API_URL}/api/chat/list`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        // Usuwamy prefiks 'chat_' dla czytelności w GUI
        const cleanChats = data.map(name => name.replace('chat_', ''));
        setChats(cleanChats);
      }
    } catch (error) {
      console.error("Błąd podczas pobierania list czatów:", error);
    }
  }, []);

  // Automatyczne odświeżanie listy czatów co 5 sekund
  useEffect(() => {
    if (authState === 'active') {
      fetchChats();
      const interval = setInterval(fetchChats, 5000);
      return () => clearInterval(interval);
    }
  }, [authState, fetchChats]);

  // 3. Obsługa tworzenia nowego czatu
  const handleCreateChat = async () => {
    if (!newChatName.trim()) return;
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`${API_URL}/api/chat/create/${newChatName.trim()}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        setNewChatName('');
        setIsModalOpen(false);
        await fetchChats(); 
        setSelectedChat(newChatName.trim()); 
      }
    } catch (error) {
      console.error("Błąd tworzenia czatu:", error);
    }
  };

  // 4. WebSocket - Połączenie i obsługa wiadomości
  useEffect(() => {
    if (authState !== 'active' || !user) return;

    // FIX: Czyścimy wiadomości natychmiast przy zmianie pokoju
    setMessages([]); 

    if (socket) socket.close();

    const token = localStorage.getItem('token');
    const ws = new WebSocket(`${WS_URL}/api/ws/chat/${selectedChat}`);
    
    ws.onopen = () => {
      setSocket(ws);
      ws.send(token); 
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'history') {
          const mappedHistory = data.messages.map((msg, idx) => ({
            id: `h-${idx}-${Date.now()}`, 
            content: msg.message,
            username: msg.username,
            timestamp: msg.timestamp,
            isOwn: msg.username === user.username
          }));
          setMessages(mappedHistory);
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
        console.error("Błąd WebSocket:", e);
      }
    };

    return () => ws.close();
  }, [authState, user, selectedChat]);

  const sendMessage = useCallback(() => {
    if (newMessage.trim() && socket) {
      socket.send(newMessage.trim()); 
      setNewMessage('');
    }
  }, [socket, newMessage]);

  // --- RENDEROWANIE ---
  if (authState === 'loading') return <div className="forum-container"><h2>Ładowanie...</h2></div>;
  if (authState === 'unauthenticated') return (
    <div className="forum-container"><button onClick={() => navigate('/login')}>Zaloguj się</button></div>
  );

  return (
    <div className="forum-container">
      {/* Sidebar */}
      <aside className="thread-list">
        <div className="thread-header">
          <h2 className="brand-logo">ryBMW</h2>
          <button className="new-thread-btn-text" onClick={() => setIsModalOpen(true)}>
            Nowy czat
          </button>
        </div>
        <div className="threads">
          {chats.map((chatName) => (
            <div 
              key={chatName} 
              className={`thread-item ${selectedChat === chatName ? 'selected' : ''}`}
              onClick={() => setSelectedChat(chatName)}
            >
              <h3>#{chatName}</h3>
            </div>
          ))}
        </div>
      </aside>

      {/* Area czatu */}
      <main className="chat-area">
        <div className="thread-title">Czat: {selectedChat}</div>
        <div className="messages">
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
        </div>
        
        <div className="message-input">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Napisz wiadomość..."
            disabled={!socket}
          />
          <button onClick={sendMessage} disabled={!socket}>Wyślij</button>
        </div>
      </main>

      {/* Modal tworzenia czatu */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Utwórz nowy czat</h3>
            <input 
              type="text" 
              placeholder="Nazwa czatu..." 
              value={newChatName}
              onChange={(e) => setNewChatName(e.target.value)}
            />
            <div className="modal-buttons">
              <button onClick={handleCreateChat}>Utwórz</button>
              <button onClick={() => setIsModalOpen(false)}>Anuluj</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Forum;