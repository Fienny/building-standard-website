const User = require('./User');
const Document = require('./Document');
const Purchase = require('./Purchase');
const Payment = require('./Payment');

// Установка связей между моделями

// User -> Purchase (One to Many)
User.hasMany(Purchase, {
  foreignKey: 'user_id',
  as: 'purchases'
});
Purchase.belongsTo(User, {
  foreignKey: 'user_id',
  as: 'user'
});

// Document -> Purchase (One to Many)
Document.hasMany(Purchase, {
  foreignKey: 'document_id',
  as: 'purchases'
});
Purchase.belongsTo(Document, {
  foreignKey: 'document_id',
  as: 'document'
});

// Purchase -> Payment (One to Many)
Purchase.hasMany(Payment, {
  foreignKey: 'purchase_id',
  as: 'payments'
});
Payment.belongsTo(Purchase, {
  foreignKey: 'purchase_id',
  as: 'purchase'
});

module.exports = {
  User,
  Document,
  Purchase,
  Payment
};
