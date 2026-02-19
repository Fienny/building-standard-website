import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import api from '../utils/api';
import './DocumentPreview.css';

function DocumentPreview() {
  const { id } = useParams();
  const { user } = useAuth();

  const [document, setDocument] = useState(null);
  const [isPurchased, setIsPurchased] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState('');
  const [loading, setLoading] = useState(true);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    api.get(`/documents/${id}`)
      .then((data) => {
        setDocument(data.document);
        setIsPurchased(data.isPurchased);
      })
      .catch(() => setDocument(null))
      .finally(() => setLoading(false));
  }, [id]);

  const handlePurchase = async () => {
    if (!user) {
      setMessage('Войдите в аккаунт для покупки документа');
      return;
    }

    if (!selectedPayment) {
      setMessage('Пожалуйста, выберите способ оплаты');
      return;
    }

    setPaymentLoading(true);
    setMessage('');

    try {
      await api.post('/payments/create', {
        document_id: parseInt(id),
        payment_method: selectedPayment,
      });
      setMessage('Платеж создан. Интеграция с платежной системой будет подключена позже.');
    } catch (err) {
      setMessage(err.message);
    } finally {
      setPaymentLoading(false);
    }
  };

  if (loading) {
    return <div className="container" style={{ padding: '60px 20px', textAlign: 'center' }}><p>Загрузка...</p></div>;
  }

  if (!document) {
    return (
      <div className="container" style={{ padding: '60px 20px', textAlign: 'center' }}>
        <h2>Документ не найден</h2>
        <Link to="/documents" className="btn btn-primary mt-3">Вернуться к документам</Link>
      </div>
    );
  }

  const previewUrl = document.file_path ? `/api/documents/${id}/preview` : null;

  return (
    <div className="preview-page">
      <div className="container">
        <div className="preview-header">
          <Link to="/documents" className="back-link">&#8592; Назад к документам</Link>
          <div className="document-info-header">
            <div>
              <h1>{document.title}</h1>
              <div className="document-meta">
                <span className="meta-badge">{document.category}</span>
                <span className="meta-item">{document.year}</span>
                <span className="meta-item">{document.pages} страниц</span>
              </div>
            </div>
            <div className="price-tag">
              <span className="price-label">Цена:</span>
              <span className="price-value">{document.price.toLocaleString('ru-RU')} сум</span>
            </div>
          </div>
          {document.description && <p className="document-description">{document.description}</p>}
        </div>

        <div className="preview-content">
          <div className="preview-section">
            <h2>Предварительный просмотр</h2>
            <p className="preview-notice">Вы можете бесплатно просмотреть первые 2 страницы документа</p>

            {previewUrl ? (
              <div className="pdf-preview">
                <iframe src={previewUrl} title="Preview" width="100%" height="800" style={{ border: '1px solid var(--border-color)', borderRadius: '8px' }} />
              </div>
            ) : (
              <div className="preview-placeholder">
                <p>Файл документа ещё не загружен. Предпросмотр будет доступен после загрузки PDF на сервер.</p>
              </div>
            )}

            {!isPurchased && (
              <div className="locked-pages">
                <div className="lock-icon">&#x1F512;</div>
                <h3>Остальные страницы доступны после оплаты</h3>
                <p>Чтобы получить полный доступ к документу, оформите покупку</p>
              </div>
            )}
          </div>

          {!isPurchased && (
            <div className="payment-section">
              <div className="payment-card">
                <h3>Купить полный документ</h3>
                <div className="payment-price">
                  <span className="price-amount">{document.price.toLocaleString('ru-RU')}</span>
                  <span className="price-currency">сум</span>
                </div>

                <div className="payment-info">
                  <p>&#10003; Полный доступ ко всем {document.pages} страницам</p>
                  <p>&#10003; Возможность скачивания в PDF</p>
                  <p>&#10003; Безлимитный просмотр</p>
                </div>

                <div className="payment-methods">
                  <h4>Способ оплаты:</h4>
                  <div className="payment-options">
                    <label className={`payment-option ${selectedPayment === 'click' ? 'selected' : ''}`}>
                      <input type="radio" name="payment" value="click"
                        checked={selectedPayment === 'click'} onChange={(e) => setSelectedPayment(e.target.value)} />
                      <span className="payment-name">Click</span>
                    </label>

                    <label className={`payment-option ${selectedPayment === 'payme' ? 'selected' : ''}`}>
                      <input type="radio" name="payment" value="payme"
                        checked={selectedPayment === 'payme'} onChange={(e) => setSelectedPayment(e.target.value)} />
                      <span className="payment-name">PayMe</span>
                    </label>

                    <label className={`payment-option ${selectedPayment === 'card' ? 'selected' : ''}`}>
                      <input type="radio" name="payment" value="card"
                        checked={selectedPayment === 'card'} onChange={(e) => setSelectedPayment(e.target.value)} />
                      <span className="payment-name">Банковская карта</span>
                    </label>
                  </div>
                </div>

                {message && <div className="payment-message">{message}</div>}

                <button onClick={handlePurchase} className="btn btn-accent w-full" disabled={paymentLoading}>
                  {paymentLoading ? 'Обработка...' : 'Оплатить'}
                </button>
              </div>
            </div>
          )}

          {isPurchased && (
            <div className="payment-section">
              <div className="payment-card">
                <h3>Документ оплачен</h3>
                <a href={`/api/documents/${id}/download`} className="btn btn-primary w-full" download>
                  Скачать полный документ
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DocumentPreview;
