import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import api from '../utils/api';
import './Profile.css';

function Profile() {
  const { user } = useAuth();
  const [purchases, setPurchases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPurchases();
  }, []);

  const loadPurchases = async () => {
    try {
      setLoading(true);
      const data = await api.get('/users/purchases');
      setPurchases(data.purchases || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (docId, docTitle) => {
    try {
      const response = await fetch(`/api/documents/${docId}/download`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Ошибка при скачивании');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${docTitle}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert(`Ошибка: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="container py-8">
        <div className="text-center">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="container">
        <div className="profile-header">
          <h1>Личный кабинет</h1>
          <div className="profile-info">
            <p><strong>Имя:</strong> {user?.name}</p>
            <p><strong>Email:</strong> {user?.email}</p>
          </div>
        </div>

        <div className="purchases-section">
          <h2>Мои покупки</h2>

          {error && <div className="error-message">{error}</div>}

          {purchases.length === 0 ? (
            <div className="empty-state">
              <p>У вас пока нет купленных документов</p>
              <Link to="/documents" className="btn btn-primary">
                Перейти к каталогу
              </Link>
            </div>
          ) : (
            <div className="purchases-list">
              {purchases.map((purchase) => (
                <div key={purchase.purchase_id} className="purchase-card">
                  <div className="purchase-info">
                    <h3>{purchase.document?.title}</h3>
                    <div className="purchase-meta">
                      <span className="category">{purchase.document?.category}</span>
                      <span className="pages">{purchase.document?.pages} страниц</span>
                      <span className="date">
                        Куплено: {new Date(purchase.purchased_at).toLocaleDateString('ru-RU')}
                      </span>
                    </div>
                    <div className="purchase-price">
                      Оплачено: {purchase.amount?.toLocaleString()} сум
                    </div>
                  </div>
                  <div className="purchase-actions">
                    <button
                      onClick={() => handleDownload(purchase.document?.id, purchase.document?.title)}
                      className="btn btn-primary"
                    >
                      📥 Скачать PDF
                    </button>
                    <Link
                      to={`/documents/${purchase.document?.id}`}
                      className="btn btn-secondary"
                    >
                      👁 Просмотр
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Profile;
