import { useState } from 'react';
import { Link } from 'react-router-dom';
import './Documents.css';

// Примеры документов для демонстрации
const mockDocuments = [
  {
    id: 1,
    title: 'ГОСТ 12.0.003-2015 ССБТ. Опасные и вредные производственные факторы',
    category: 'Безопасность труда',
    year: 2015,
    pages: 15,
    price: 50000
  },
  {
    id: 2,
    title: 'ГОСТ 8.417-2002 Единицы величин',
    category: 'Метрология',
    year: 2002,
    pages: 28,
    price: 45000
  },
  {
    id: 3,
    title: 'ГОСТ 2.105-95 ЕСКД. Общие требования к текстовым документам',
    category: 'Документация',
    year: 1995,
    pages: 32,
    price: 55000
  },
  {
    id: 4,
    title: 'ГОСТ 21.101-97 СПДС. Основные требования к проектной документации',
    category: 'Проектирование',
    year: 1997,
    pages: 45,
    price: 75000
  },
  {
    id: 5,
    title: 'ГОСТ Р 57276-2016 Безопасность грузоподъемных кранов',
    category: 'Безопасность',
    year: 2016,
    pages: 52,
    price: 85000
  },
  {
    id: 6,
    title: 'ГОСТ 34.602-89 Техническое задание. Требования к содержанию',
    category: 'ИТ и автоматизация',
    year: 1989,
    pages: 18,
    price: 40000
  }
];

function Documents() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = ['all', ...new Set(mockDocuments.map(doc => doc.category))];

  const filteredDocuments = mockDocuments.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || doc.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

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
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="category-filters">
            {categories.map(category => (
              <button
                key={category}
                className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
                onClick={() => setSelectedCategory(category)}
              >
                {category === 'all' ? 'Все категории' : category}
              </button>
            ))}
          </div>
        </div>

        <div className="documents-grid">
          {filteredDocuments.length > 0 ? (
            filteredDocuments.map(doc => (
              <div key={doc.id} className="document-card">
                <div className="document-header">
                  <span className="document-category">{doc.category}</span>
                  <span className="document-year">{doc.year}</span>
                </div>
                <h3 className="document-title">{doc.title}</h3>
                <div className="document-info">
                  <span>📄 {doc.pages} страниц</span>
                  <span className="document-price">{doc.price.toLocaleString('ru-RU')} сум</span>
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
      </div>
    </div>
  );
}

export default Documents;
