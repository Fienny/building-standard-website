const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Payment = sequelize.define('Payment', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  purchase_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: 'purchases',
      key: 'id'
    }
  },
  payment_system: {
    type: DataTypes.ENUM('click', 'payme', 'card'),
    allowNull: false
  },
  transaction_id: {
    type: DataTypes.STRING(255),
    allowNull: true,
    unique: true
  },
  amount: {
    type: DataTypes.INTEGER,
    allowNull: false,
    comment: 'Сумма в сумах'
  },
  status: {
    type: DataTypes.ENUM('pending', 'processing', 'completed', 'failed', 'cancelled'),
    defaultValue: 'pending'
  },
  payment_url: {
    type: DataTypes.TEXT,
    allowNull: true,
    comment: 'URL для перенаправления на оплату'
  },
  callback_data: {
    type: DataTypes.JSONB,
    allowNull: true,
    comment: 'Данные от платежной системы'
  },
  error_message: {
    type: DataTypes.TEXT,
    allowNull: true
  }
}, {
  tableName: 'payments',
  timestamps: true
});

module.exports = Payment;
