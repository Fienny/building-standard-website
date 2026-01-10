const jwt = require('jsonwebtoken');
const { User } = require('../models');

// Middleware для проверки JWT токена
const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      return res.status(401).json({
        error: 'Токен не предоставлен'
      });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // Получаем пользователя из БД
    const user = await User.findByPk(decoded.userId);

    if (!user) {
      return res.status(401).json({
        error: 'Пользователь не найден'
      });
    }

    if (!user.is_active) {
      return res.status(403).json({
        error: 'Аккаунт деактивирован'
      });
    }

    // Добавляем пользователя в req
    req.user = user;
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        error: 'Токен истек'
      });
    }

    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        error: 'Недействительный токен'
      });
    }

    return res.status(500).json({
      error: 'Ошибка аутентификации'
    });
  }
};

// Middleware для проверки роли администратора
const requireAdmin = (req, res, next) => {
  if (req.user.role !== 'admin') {
    return res.status(403).json({
      error: 'Доступ запрещен. Требуются права администратора'
    });
  }
  next();
};

// Опциональная аутентификация (не выдает ошибку, если токена нет)
const optionalAuth = async (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token) {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      const user = await User.findByPk(decoded.userId);
      if (user && user.is_active) {
        req.user = user;
      }
    }
  } catch (error) {
    // Игнорируем ошибки для опциональной аутентификации
  }
  next();
};

module.exports = {
  authenticateToken,
  requireAdmin,
  optionalAuth
};
