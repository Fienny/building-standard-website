import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../utils/api';
import './Documents.css';

function Documents() {
  const [documents, setDocuments] = useState([]);
  const [categories, setCategories] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const timerId = setTimeout(() => {
      setDebouncedSearch(searchQuery.trim());
    }, 300);

    return () => clearTimeout(timerId);
  }, [searchQuery]);

  useEffect(() => {
    api.get('/documents/categories')
      .then((data) => setCategories(data.categories || []))
      .catch(() => setCategories([]));
  }, []);

  useEffect(() => {
    const params = new URLSearchParams();
    if (debouncedSearch) {
      params.set('search', debouncedSearch);
    }
    if (selectedCategory !== 'all') {
      params.set('category', selectedCategory);
    }

    api.get(`/documents?${params.toString()}`)
      .then((data) => setDocuments(Array.isArray(data.documents) ? data.documents : []))
      .catch(() => {
        setDocuments([]);
        setError('Не удалось загрузить документы. Проверьте соединение и попробуйте снова.');
      })
      .finally(() => setLoading(false));
  }, [debouncedSearch, selectedCategory]);

  return (
    <div className="documents-page">
      <div className="container">
        <div className="documents-header">
          <h1>База государственных стандартов</h1>
          <p>Найдите нужный документ в нашей базе данных</p>
        </div>

        <div className="documents-filters">
          <div className="search-box">
            <input
              type="text"
              placeholder="Поиск по названию документа..."
              value={searchQuery}
              onChange={(event) => {
                setError('');
                setLoading(true);
                setSearchQuery(event.target.value);
              }}
              className="search-input"
            />
          </div>

          <div className="category-filters">
            <button
              className={`category-btn ${selectedCategory === 'all' ? 'active' : ''}`}
              onClick={() => {
              setError('');
              setLoading(true);
              setSelectedCategory('all');
            }}
            >
              Все категории
            </button>
            {categories.map((category) => (
              <button
                key={category}
                className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
                onClick={() => {
                  setError('');
                  setLoading(true);
                  setSelectedCategory(category);
                }}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="no-results"><p>Загрузка...</p></div>
        ) : error ? (
          <div className="no-results"><p>{error}</p></div>
        ) : (
          <div className="documents-grid">
            {documents.length > 0 ? (
              documents.map((doc) => (
                <div key={doc.id} className="document-card">
                  <div className="document-header">
                    <span className="document-category">{doc.category || 'Без категории'}</span>
                    <span className="document-year">{doc.year || '—'}</span>
                  </div>
                  <h3 className="document-title">{doc.title}</h3>
                  <div className="document-info">
                    <span>{doc.pages || 0} стр.</span>
                    <span className="document-price">{Number(doc.price || 0).toLocaleString('ru-RU')} сум</span>
                  </div>
                  <Link to={`/documents/${doc.id}`} className="btn btn-primary w-full">
                    Просмотр документа
                  </Link>
                </div>
              ))
            ) : (
              <div className="no-results">
                <p>Документы не найдены</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Documents;
