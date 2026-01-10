const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Purchase = sequelize.define('Purchase', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  user_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    }
  },
  document_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: 'documents',
      key: 'id'
    }
  },
  amount: {
    type: DataTypes.INTEGER,
    allowNull: false,
    comment: 'Сумма в сумах'
  },
  payment_method: {
    type: DataTypes.ENUM('click', 'payme', 'card'),
    allowNull: false
  },
  payment_status: {
    type: DataTypes.ENUM('pending', 'processing', 'completed', 'failed', 'refunded'),
    defaultValue: 'pending'
  },
  transaction_id: {
    type: DataTypes.STRING(255),
    allowNull: true,
    unique: true
  }
}, {
  tableName: 'purchases',
  timestamps: true
});

module.exports = Purchase;
