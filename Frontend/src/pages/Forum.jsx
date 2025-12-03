import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL, WS_URL } from '../config';
import '../App.css';

// WebSocket URL - now using environment variable
const WS_CHAT_URL = `${WS_URL}/api/ws/chat`; 

// The single, fixed ID for the main chat thread
const MAIN_THREAD_ID = 1;

function Forum() {
  // --- STATE AND HOOKS ---
  const [authState, setAuthState] = useState('loading');
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  // Reference for auto-scrolling
  const messagesEndRef = useRef(null); 
  
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  
  // Define required state variables for logic, even if the UI is simplified
  const [threads, setThreads] = useState([]); 
  const [selectedThread, setSelectedThread] = useState(MAIN_THREAD_ID);

  const currentMessages = useMemo(() => messages.filter(msg => msg.threadId === selectedThread), [messages, selectedThread]);


  // ----------------------------------------------------------------------
  // --- NEW SCROLL EFFECT ---
  // ----------------------------------------------------------------------
  useEffect(() => {
    // This function scrolls the referenced element (the messages div) to its bottom
    const scrollToBottom = () => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    scrollToBottom();
  }, [messages]); // Trigger whenever the messages list changes


  // ----------------------------------------------------------------------
  // --- AUTHENTICATION AND INITIAL USER FETCH ---
  // ----------------------------------------------------------------------
  useEffect(() => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      setAuthState('unauthenticated');
      return;
    }

    const fetchUser = async () => {
      try {
        const response = await fetch(`${API_URL}/api/users/me`, {
          method: 'GET',
          headers: {
            'accept': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (response.status === 401) {
          localStorage.removeItem('token');
          setAuthState('unauthenticated');
          return;
        }

        if (!response.ok) {
          throw new Error('Failed to fetch user data');
        }

        const userData = await response.json();
        setUser(userData);

        if (userData.is_active) {
          setAuthState('active');
        } else {
          setAuthState('locked');
        }
      } catch (error) {
        console.error("Authentication Error:", error);
        setAuthState('unauthenticated');
      }
    };

    fetchUser();
  }, [navigate]);

  // ----------------------------------------------------------------------
  // --- WEBSOCKET CONNECTION ---
  // ----------------------------------------------------------------------
  useEffect(() => {
    if (authState !== 'active') {
      if (socket) socket.close();
      return;
    }

    const token = localStorage.getItem('token');
    const ws = new WebSocket(WS_CHAT_URL);
    
    ws.onopen = () => {
      console.log('Connected to WebSocket');
      setSocket(ws);
      ws.send(token); 
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'auth_failed') {
          console.error("WebSocket Authentication Failed:", data.detail || "Invalid token.");
          setAuthState('unauthenticated');
          ws.close();
        } 
        else if (data.type === 'history' && user) {
          const mappedHistory = data.messages.map((msg, index) => ({
            id: `h-${index}-${Date.now()}`, 
            threadId: selectedThread, 
            content: msg.message,
            username: msg.username,
            timestamp: msg.timestamp,
            isOwn: msg.username === user.username
          }));
          setMessages(mappedHistory);
        } 
        else if (data.type === 'message' && user) {
          const newMessageObject = {
            id: Date.now(), 
            threadId: selectedThread,
            content: data.message,
            username: data.username,
            timestamp: data.timestamp,
            isOwn: data.username === user.username
          };
          setMessages(prev => [...prev, newMessageObject]);
        }
        else if (data.type === 'thread_list') {
            setThreads(data.threads); 
        }
      } catch (e) {
          console.error("Error parsing WebSocket message:", e, event.data);
      }
    };

    ws.onclose = () => {
      console.log('Disconnected from WebSocket');
      setSocket(null);
    };

    return () => {
      ws.close();
    };
  }, [authState, user, selectedThread]);

// ----------------------------------------------------------------------
// --- MESSAGE SENDING ---
// ----------------------------------------------------------------------
  const sendMessage = useCallback(() => {
    if (newMessage.trim() && selectedThread && socket) {
      // Send the message content as plain text
      socket.send(newMessage.trim()); 
      setNewMessage('');
    }
  }, [socket, newMessage, selectedThread]);


  // ----------------------------------------------------------------------
  // --- CONDITIONAL RENDERING ---
  // ----------------------------------------------------------------------

  if (authState === 'loading') {
    return <div className="forum-container"><h2>Ładowanie...</h2></div>;
  }

  if (authState === 'unauthenticated') {
    return (
      <div className="forum-container">
        <div className="no-thread-selected">
          <h2>Błąd autoryzacji</h2>
          <p>Proszę, zaloguj się, aby uzyskać dostęp do forum.</p>
          <button onClick={() => navigate('/login')}>Przejdź do logowania</button>
        </div>
      </div>
    );
  }

  if (authState === 'locked') {
    return (
      <div className="forum-container">
        <div className="no-thread-selected">
          <h2>Konto Zablokowane</h2>
          <p>Twoje konto jest nieaktywne lub zostało zablokowane. Skontaktuj się z administratorem.</p>
        </div>
      </div>
    );
  }

  // --- MAIN FORUM UI (Active State) ---
  return (
    <div className="forum-container">
      <aside className="thread-list">
        <div className="thread-header">
          <h2>Forum ryBMW</h2>
        </div>
        <div className="threads">
          <div className="thread-item selected">
            <h3>Główny wątek</h3>
            <p>Wątek powitalny (Zalogowany jako: **{user?.username}**)</p>
          </div>
        </div>
      </aside>

      <main className="chat-area">
        <>
          <div className="thread-title">
            Główny wątek
          </div>
          {/* Apply the ref to the messages container */}
          <div className="messages">
            {currentMessages.map((message, index) => (
              <div key={message.id || index} className={`message ${message.isOwn ? "own" : ""}`}> 
                <div className="message-header">
                  <span className="username">{message.username}</span>
                  <span className="timestamp">{new Date(message.timestamp).toLocaleTimeString()}</span>
                </div>
                <p>{message.content}</p>
              </div>
            ))}
            {/* Add a dummy div at the end to scroll into view */}
            <div ref={messagesEndRef} />
          </div>
          
          <div className="message-input">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder={socket ? "Type your message..." : "Łączenie z czatem..."}
              disabled={!socket}
            />
            <button onClick={sendMessage} disabled={!socket}>
              {socket ? 'Wyślij' : 'Łączenie...'}
            </button>
          </div>
        </>
      </main>
    </div>
  );
}

export default Forum;