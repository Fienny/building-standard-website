const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Document = sequelize.define('Document', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  title: {
    type: DataTypes.STRING(500),
    allowNull: false,
    validate: {
      notEmpty: {
        msg: 'Название документа не может быть пустым'
      }
    }
  },
  category: {
    type: DataTypes.STRING(100),
    allowNull: false
  },
  year: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: {
        args: [1900],
        msg: 'Год должен быть больше 1900'
      },
      max: {
        args: [new Date().getFullYear() + 1],
        msg: 'Год не может быть в будущем'
      }
    }
  },
  pages: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: {
        args: [1],
        msg: 'Количество страниц должно быть больше 0'
      }
    }
  },
  price: {
    type: DataTypes.INTEGER,
    allowNull: false,
    comment: 'Цена в сумах',
    validate: {
      min: {
        args: [0],
        msg: 'Цена не может быть отрицательной'
      }
    }
  },
  description: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  file_path: {
    type: DataTypes.STRING(500),
    allowNull: true,
    comment: 'Путь к полному PDF файлу'
  },
  preview_path: {
    type: DataTypes.STRING(500),
    allowNull: true,
    comment: 'Путь к preview PDF (первые 2 страницы)'
  },
  is_active: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  },
  download_count: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  }
}, {
  tableName: 'documents',
  timestamps: true
});

module.exports = Document;
