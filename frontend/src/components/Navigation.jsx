import { Link } from 'react-router-dom';
import './Navigation.css';

function Navigation() {
  return (
    <nav className="navigation">
      <div className="container">
        <div className="nav-content">
          <Link to="/" className="logo">
            <h2>Стандарты РУз</h2>
          </Link>
          <div className="nav-links">
            <Link to="/documents" className="nav-link">Документы</Link>
            <Link to="/login" className="nav-link btn btn-primary">Войти</Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;
