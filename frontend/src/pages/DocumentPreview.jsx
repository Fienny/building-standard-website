import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import api from '../utils/api';
import './DocumentPreview.css';

const PAYMENT_LABELS = {
  click: 'Click',
  payme: 'PayMe',
  card: 'Банковская карта',
};

function formatPrice(value) {
  const numericPrice = Number(value);
  if (Number.isNaN(numericPrice)) {
    return '—';
  }
  return numericPrice.toLocaleString('ru-RU');
}

function DocumentPreview() {
  const { id } = useParams();
  const { user } = useAuth();

  const [document, setDocument] = useState(null);
  const [isPurchased, setIsPurchased] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState('');
  const [loading, setLoading] = useState(true);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('info');
  const [paymentUrl, setPaymentUrl] = useState('');

  useEffect(() => {
    let cancelled = false;

    const loadDocument = async () => {
      try {
        const data = await api.get(`/documents/${id}`);
        if (cancelled) {
          return;
        }
        setDocument(data.document || null);
        setIsPurchased(Boolean(data.isPurchased));
      } catch {
        if (!cancelled) {
          setDocument(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadDocument();

    return () => {
      cancelled = true;
    };
  }, [id]);

  const setFeedback = (text, type = 'info') => {
    setMessage(text);
    setMessageType(type);
  };

  const handlePurchase = async () => {
    if (!user) {
      setFeedback('Войдите в аккаунт для покупки документа.', 'warning');
      return;
    }

    if (!selectedPayment) {
      setFeedback('Пожалуйста, выберите способ оплаты.', 'warning');
      return;
    }

    setPaymentLoading(true);
    setMessage('');
    setPaymentUrl('');

    try {
      const payload = await api.post('/payments/create', {
        document_id: Number.parseInt(id, 10),
        payment_method: selectedPayment,
      });

      const nextPaymentUrl = payload?.payment_url;
      if (nextPaymentUrl) {
        setPaymentUrl(nextPaymentUrl);
        setFeedback(
          `Платёж создан через ${PAYMENT_LABELS[selectedPayment]}. Откройте страницу провайдера для завершения оплаты.`,
          'success',
        );
      } else {
        setFeedback(
          'Платёж создан, но ссылка провайдера не получена. Обратитесь к администратору.',
          'warning',
        );
      }
    } catch (err) {
      setFeedback(err.message || 'Не удалось создать платёж. Попробуйте позже.', 'error');
    } finally {
      setPaymentLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ padding: '60px 20px', textAlign: 'center' }}>
        <p>Загрузка...</p>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="container" style={{ padding: '60px 20px', textAlign: 'center' }}>
        <h2>Документ не найден</h2>
        <Link to="/documents" className="btn btn-primary mt-3">
          Вернуться к документам
        </Link>
      </div>
    );
  }

  const previewUrl = document.file_path ? `/api/documents/${id}/preview` : null;

  return (
    <div className="preview-page">
      <div className="container">
        <div className="preview-header">
          <Link to="/documents" className="back-link">
            &#8592; Назад к документам
          </Link>
          <div className="document-info-header">
            <div>
              <h1>{document.title}</h1>
              <div className="document-meta">
                <span className="meta-badge">{document.category || 'Без категории'}</span>
                {document.year ? <span className="meta-item">{document.year}</span> : null}
                <span className="meta-item">{document.pages || 0} страниц</span>
              </div>
            </div>
            <div className="price-tag">
              <span className="price-label">Цена:</span>
              <span className="price-value">{formatPrice(document.price)} сум</span>
            </div>
          </div>
          {document.description && <p className="document-description">{document.description}</p>}
        </div>

        <div className="preview-content">
          <div className="preview-section">
            <h2>Предварительный просмотр</h2>
            <p className="preview-notice">Вы можете бесплатно просмотреть первые 2 страницы документа.</p>

            {previewUrl ? (
              <div className="pdf-preview">
                <iframe
                  src={previewUrl}
                  title="Preview"
                  width="100%"
                  height="800"
                  style={{ border: '1px solid var(--border-color)', borderRadius: '8px' }}
                />
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
                <p>Чтобы получить полный доступ к документу, оформите покупку.</p>
              </div>
            )}
          </div>

          {!isPurchased && (
            <div className="payment-section">
              <div className="payment-card">
                <h3>Купить полный документ</h3>
                <div className="payment-price">
                  <span className="price-amount">{formatPrice(document.price)}</span>
                  <span className="price-currency">сум</span>
                </div>

                <div className="payment-info">
                  <p>&#10003; Полный доступ ко всем {document.pages || 0} страницам</p>
                  <p>&#10003; Возможность скачивания в PDF</p>
                  <p>&#10003; Безлимитный просмотр</p>
                </div>

                <div className="payment-methods">
                  <h4>Способ оплаты:</h4>
                  <div className="payment-options">
                    {Object.entries(PAYMENT_LABELS).map(([method, label]) => (
                      <label
                        key={method}
                        className={`payment-option ${selectedPayment === method ? 'selected' : ''}`}
                      >
                        <input
                          type="radio"
                          name="payment"
                          value={method}
                          checked={selectedPayment === method}
                          onChange={(event) => setSelectedPayment(event.target.value)}
                        />
                        <span className="payment-name">{label}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {message && <div className={`payment-message payment-message-${messageType}`}>{message}</div>}

                {paymentUrl && (
                  <a className="btn btn-primary w-full" href={paymentUrl} target="_blank" rel="noopener noreferrer">
                    Перейти к оплате
                  </a>
                )}

                <button
                  onClick={handlePurchase}
                  className="btn btn-accent w-full mt-2"
                  disabled={paymentLoading}
                >
                  {paymentLoading ? 'Создание платежа...' : 'Создать платеж'}
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
