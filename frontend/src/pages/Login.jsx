import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import './Auth.css';

function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(formData.email, formData.password);
      navigate('/documents');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <h1 className="auth-title">Вход в аккаунт</h1>
          <p className="auth-subtitle">Войдите, чтобы получить доступ к документам</p>

          {error && <div className="auth-error">{error}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="email">Электронная почта</label>
              <input type="email" id="email" name="email" value={formData.email}
                onChange={handleChange} required placeholder="example@mail.com" className="form-input" />
            </div>

            <div className="form-group">
              <label htmlFor="password">Пароль</label>
              <input type="password" id="password" name="password" value={formData.password}
                onChange={handleChange} required placeholder="••••••••" className="form-input" />
            </div>

            <button type="submit" className="btn btn-primary w-full" disabled={loading}>
              {loading ? 'Вход...' : 'Войти'}
            </button>
          </form>

          <div className="auth-footer">
            <p>Нет аккаунта? <Link to="/signup" className="auth-link">Зарегистрироваться</Link></p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
