import { Link, useSearchParams } from 'react-router-dom';
import './PaymentResult.css';

const STATUS_CONTENT = {
  success: {
    title: 'Платёж создан',
    description:
      'Мы зарегистрировали заявку на оплату. После подтверждения провайдером документ автоматически станет доступен в полном объёме.',
    note: 'Если оплата уже выполнена, обновите страницу документа через 10–30 секунд.',
    badgeClass: 'payment-status-success',
  },
  failed: {
    title: 'Платёж не завершён',
    description:
      'Оплата была отменена или завершилась ошибкой. Вы можете вернуться к документу и попробовать другой способ оплаты.',
    note: 'Деньги не должны списаться при статусе отказа. При списании — обратитесь в поддержку.',
    badgeClass: 'payment-status-failed',
  },
  pending: {
    title: 'Проверяем статус оплаты',
    description:
      'Провайдер ещё не отправил финальный callback. Обычно это занимает до 1 минуты.',
    note: 'Вы можете подождать и обновить страницу, либо вернуться к документу.',
    badgeClass: 'payment-status-pending',
  },
};

function PaymentResult({ status = 'pending' }) {
  const [searchParams] = useSearchParams();
  const purchaseId = searchParams.get('purchase_id');
  const content = STATUS_CONTENT[status] || STATUS_CONTENT.pending;

  return (
    <div className="payment-result-page">
      <div className="container">
        <div className="payment-result-card">
          <span className={`payment-status-badge ${content.badgeClass}`}>{status.toUpperCase()}</span>
          <h1>{content.title}</h1>
          <p className="payment-result-description">{content.description}</p>
          <p className="payment-result-note">{content.note}</p>

          {purchaseId && (
            <p className="payment-result-meta">
              Purchase ID: <strong>{purchaseId}</strong>
            </p>
          )}

          <div className="payment-result-actions">
            <Link to="/documents" className="btn btn-primary">
              К документам
            </Link>
            <Link to="/" className="btn btn-secondary">
              На главную
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PaymentResult;
