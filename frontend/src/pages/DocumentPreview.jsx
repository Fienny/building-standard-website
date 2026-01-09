import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import './DocumentPreview.css';

// Mock data для демонстрации
const mockDocuments = {
  1: {
    id: 1,
    title: 'ГОСТ 12.0.003-2015 ССБТ. Опасные и вредные производственные факторы',
    category: 'Безопасность труда',
    year: 2015,
    pages: 15,
    price: 50000,
    description: 'Стандарт устанавливает классификацию опасных и вредных производственных факторов.'
  },
  2: {
    id: 2,
    title: 'ГОСТ 8.417-2002 Единицы величин',
    category: 'Метрология',
    year: 2002,
    pages: 28,
    price: 45000,
    description: 'Настоящий стандарт устанавливает единицы физических величин, применяемые в Республике Узбекистан.'
  }
};

function DocumentPreview() {
  const { id } = useParams();
  const [selectedPayment, setSelectedPayment] = useState('');
  const document = mockDocuments[id];

  if (!document) {
    return (
      <div className="container" style={{ padding: '60px 20px', textAlign: 'center' }}>
        <h2>Документ не найден</h2>
        <Link to="/documents" className="btn btn-primary mt-3">Вернуться к документам</Link>
      </div>
    );
  }

  const handlePurchase = () => {
    if (!selectedPayment) {
      alert('Пожалуйста, выберите способ оплаты');
      return;
    }
    // TODO: Implement payment logic
    alert(`Оплата через ${selectedPayment}. Функционал будет реализован позже.`);
  };

  return (
    <div className="preview-page">
      <div className="container">
        <div className="preview-header">
          <Link to="/documents" className="back-link">← Назад к документам</Link>
          <div className="document-info-header">
            <div>
              <h1>{document.title}</h1>
              <div className="document-meta">
                <span className="meta-badge">{document.category}</span>
                <span className="meta-item">📅 {document.year}</span>
                <span className="meta-item">📄 {document.pages} страниц</span>
              </div>
            </div>
            <div className="price-tag">
              <span className="price-label">Цена:</span>
              <span className="price-value">{document.price.toLocaleString('ru-RU')} сум</span>
            </div>
          </div>
          <p className="document-description">{document.description}</p>
        </div>

        <div className="preview-content">
          <div className="preview-section">
            <h2>Предварительный просмотр</h2>
            <p className="preview-notice">Вы можете бесплатно просмотреть первые 2 страницы документа</p>

            {/* Страница 1 */}
            <div className="preview-page-container">
              <div className="page-header">Страница 1</div>
              <div className="page-content">
                <h3>{document.title}</h3>
                <div className="page-text">
                  <p><strong>1. ОБЛАСТЬ ПРИМЕНЕНИЯ</strong></p>
                  <p>Настоящий стандарт устанавливает основные понятия, термины и определения в области, указанной в названии стандарта.</p>
                  <p>Термины, установленные настоящим стандартом, обязательны для применения во всех видах документации и литературы, входящих в сферу действия работ по стандартизации или использующих результаты этих работ.</p>
                  <p><strong>2. НОРМАТИВНЫЕ ССЫЛКИ</strong></p>
                  <p>В настоящем стандарте использованы нормативные ссылки на следующие стандарты:</p>
                  <ul>
                    <li>ГОСТ 12.0.002-2003 ССБТ. Термины и определения</li>
                    <li>ГОСТ 12.1.003-2014 ССБТ. Шум. Общие требования безопасности</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Страница 2 */}
            <div className="preview-page-container">
              <div className="page-header">Страница 2</div>
              <div className="page-content">
                <div className="page-text">
                  <p><strong>3. ТЕРМИНЫ И ОПРЕДЕЛЕНИЯ</strong></p>
                  <p>В настоящем стандарте применены следующие термины с соответствующими определениями:</p>
                  <p><strong>3.1 опасный производственный фактор:</strong> Производственный фактор, воздействие которого на работника может привести к его травме.</p>
                  <p><strong>3.2 вредный производственный фактор:</strong> Производственный фактор, воздействие которого на работника может привести к его заболеванию.</p>
                  <p><strong>3.3 безопасные условия труда:</strong> Условия труда, при которых воздействие на работающих вредных и (или) опасных производственных факторов исключено либо уровни их воздействия не превышают установленных нормативов.</p>
                </div>
              </div>
            </div>

            {/* Блокировка остальных страниц */}
            <div className="locked-pages">
              <div className="lock-icon">🔒</div>
              <h3>Остальные страницы доступны после оплаты</h3>
              <p>Чтобы получить полный доступ к документу, оформите покупку</p>
            </div>
          </div>

          {/* Блок оплаты */}
          <div className="payment-section">
            <div className="payment-card">
              <h3>Купить полный документ</h3>
              <div className="payment-price">
                <span className="price-amount">{document.price.toLocaleString('ru-RU')}</span>
                <span className="price-currency">сум</span>
              </div>

              <div className="payment-info">
                <p>✓ Полный доступ ко всем {document.pages} страницам</p>
                <p>✓ Возможность скачивания в PDF</p>
                <p>✓ Безлимитный просмотр</p>
              </div>

              <div className="payment-methods">
                <h4>Способ оплаты:</h4>
                <div className="payment-options">
                  <label className={`payment-option ${selectedPayment === 'click' ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      name="payment"
                      value="click"
                      checked={selectedPayment === 'click'}
                      onChange={(e) => setSelectedPayment(e.target.value)}
                    />
                    <span className="payment-name">Click</span>
                  </label>

                  <label className={`payment-option ${selectedPayment === 'payme' ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      name="payment"
                      value="payme"
                      checked={selectedPayment === 'payme'}
                      onChange={(e) => setSelectedPayment(e.target.value)}
                    />
                    <span className="payment-name">PayMe</span>
                  </label>

                  <label className={`payment-option ${selectedPayment === 'card' ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      name="payment"
                      value="card"
                      checked={selectedPayment === 'card'}
                      onChange={(e) => setSelectedPayment(e.target.value)}
                    />
                    <span className="payment-name">Банковская карта</span>
                  </label>
                </div>
              </div>

              <button onClick={handlePurchase} className="btn btn-accent w-full">
                Оплатить
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DocumentPreview;
