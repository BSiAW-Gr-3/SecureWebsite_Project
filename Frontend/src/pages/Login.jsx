import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

// Assuming these paths are correct for your project structure
import loginPic from '../assets/login_pic.jpg';
import bmwLogo from '../assets/rybmw.jpg';
import { API_URL } from '../config';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/token`, {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/x-www-form-urlencoded', 
        },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`, 
        credentials: 'include', 
      });

      // 1. Get the JSON data (which contains access_token)
      const data = await response.json(); 

      if (!response.ok) {
        throw new Error(data.detail || 'Błąd logowania'); 
      }
      
      // 2. Client-side storage of the token
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('token_type', data.token_type || 'Bearer');
      }

      // 3. Successful login: Navigate to the forum
      navigate('/forum'); 

    } catch (err) {
      // 4. Handle and display errors
      setError(err.message || 'Wystąpił błąd podczas logowania'); 
    } finally {
      // 5. Clear loading state
      setIsLoading(false); 
    }
  }

  return (
    <div className="login-container">
      {/* Image container for visual layout */}
      <div className="login-image" aria-hidden>
        <img
          src={loginPic}
          alt="Ilustracja logowania"
        />
      </div>
      
      {/* Login form layout */}
      <div className="login-layout">
        <form onSubmit={handleSubmit} className="login-form">
          <div className="logo-container">
            <img src={bmwLogo} alt="BMW Logo" className="bmw-logo" />
          </div>
          
          {/* Error Message Display (Conditional Rendering) */}
          {error && <div className="error-message">{error}</div>}
          
          {/* Username Input */}
          <div className="form-group">
            <label htmlFor="username">Nazwa użytkownika:</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
          
          {/* Password Input */}
          <div className="form-group">
            <label htmlFor="password">Hasło:</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
          
          {/* Submit Button */}
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Logowanie...' : 'Zaloguj się'}
          </button>
          
          {/* Footer Links */}
          <p className="form-footer">
            Nie masz konta? <Link to="/register">Zarejestruj się</Link>
          </p>
        </form>
      </div>
    </div>
  )
}

export default Login;