import { Link } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import AIAssistant from '../components/AIAssistant';
import './Home.css';

function Home() {
  const { user } = useAuth();

  return (
    <div className="home">
      <AIAssistant />

      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <h1>Государственные стандарты Республики Узбекистан</h1>
            <p className="hero-subtitle">
              Полный доступ к актуальным государственным стандартам на русском языке.
              Профессиональный перевод, удобный поиск, AI-помощник для работы с документами.
            </p>
            <div className="hero-buttons">
              <Link to="/documents" className="btn btn-accent">Смотреть документы</Link>
              {!user && <Link to="/signup" className="btn btn-primary">Зарегистрироваться</Link>}
            </div>
          </div>
        </div>
      </section>

      <section className="stats">
        <div className="container">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-number">90+</div>
              <div className="stat-label">Документов</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">3</div>
              <div className="stat-label">Категории</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">24/7</div>
              <div className="stat-label">AI Помощник</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">100%</div>
              <div className="stat-label">Актуальность</div>
            </div>
          </div>
        </div>
      </section>

      <section className="features">
        <div className="container">
          <h2 className="section-title">Почему выбирают нас</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">📄</div>
              <h3>Актуальные документы</h3>
              <p>Постоянно обновляемая база государственных стандартов РУз</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🌐</div>
              <h3>Профессиональный перевод</h3>
              <p>Качественный перевод на русский язык от сертифицированных специалистов</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">👁️</div>
              <h3>Предпросмотр</h3>
              <p>Бесплатный просмотр первых 2 страниц каждого документа</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">💳</div>
              <h3>Удобная оплата</h3>
              <p>Поддержка Click, PayMe и банковских карт</p>
            </div>
          </div>
        </div>
      </section>

      {!user && (
        <section className="cta">
          <div className="container">
            <div className="cta-content">
              <h2>Начните работать со стандартами сегодня</h2>
              <p>Зарегистрируйтесь и получите доступ к полной базе документов</p>
              <Link to="/signup" className="btn btn-accent">Создать аккаунт</Link>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

export default Home;
