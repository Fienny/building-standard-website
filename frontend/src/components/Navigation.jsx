import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import './Navigation.css';

function Navigation() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navigation">
      <div className="container">
        <div className="nav-content">
          <Link to="/" className="logo">
            <h2>Стандарты РУз</h2>
          </Link>
          <div className="nav-links">
            <Link to="/documents" className="nav-link">Документы</Link>
            {user ? (
              <>
                <span className="nav-user">{user.name}</span>
                <button onClick={handleLogout} className="nav-link btn btn-secondary">Выйти</button>
              </>
            ) : (
              <Link to="/login" className="nav-link btn btn-primary">Войти</Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;
