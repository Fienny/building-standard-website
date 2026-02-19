import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import './Auth.css';

function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '', email: '', password: '', confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    setLoading(true);
    try {
      await signup(formData.name, formData.email, formData.password);
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
          <h1 className="auth-title">Регистрация</h1>
          <p className="auth-subtitle">Создайте аккаунт для доступа к стандартам</p>

          {error && <div className="auth-error">{error}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="name">Имя</label>
              <input type="text" id="name" name="name" value={formData.name}
                onChange={handleChange} required placeholder="Иван Иванов" className="form-input" />
            </div>

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

            <div className="form-group">
              <label htmlFor="confirmPassword">Подтвердите пароль</label>
              <input type="password" id="confirmPassword" name="confirmPassword" value={formData.confirmPassword}
                onChange={handleChange} required placeholder="••••••••" className="form-input" />
            </div>

            <button type="submit" className="btn btn-primary w-full" disabled={loading}>
              {loading ? 'Регистрация...' : 'Зарегистрироваться'}
            </button>
          </form>

          <div className="auth-footer">
            <p>Уже есть аккаунт? <Link to="/login" className="auth-link">Войти</Link></p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Signup;
