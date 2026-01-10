const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const { User } = require('../models');
const { authenticateToken } = require('../middleware/auth');

// Генерация JWT токена
const generateToken = (userId) => {
  return jwt.sign(
    { userId },
    process.env.JWT_SECRET,
    { expiresIn: process.env.JWT_EXPIRE || '24h' }
  );
};

// POST /api/auth/register - Регистрация
router.post('/register', [
  body('email').isEmail().withMessage('Некорректный email'),
  body('password').isLength({ min: 6 }).withMessage('Пароль должен быть минимум 6 символов'),
  body('name').notEmpty().withMessage('Имя обязательно')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, password, name } = req.body;

    // Проверка существующего пользователя
    const existingUser = await User.findOne({ where: { email } });
    if (existingUser) {
      return res.status(400).json({
        error: 'Пользователь с таким email уже существует'
      });
    }

    // Создание пользователя
    const user = await User.create({ email, name });
    await user.setPassword(password);
    await user.save();

    // Генерация токена
    const token = generateToken(user.id);

    res.status(201).json({
      message: 'Регистрация успешна',
      token,
      user: user.toJSON()
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({
      error: 'Ошибка при регистрации'
    });
  }
});

// POST /api/auth/login - Вход
router.post('/login', [
  body('email').isEmail().withMessage('Некорректный email'),
  body('password').notEmpty().withMessage('Пароль обязателен')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, password } = req.body;

    // Поиск пользователя
    const user = await User.findOne({ where: { email } });
    if (!user) {
      return res.status(401).json({
        error: 'Неверный email или пароль'
      });
    }

    // Проверка пароля
    const isValidPassword = await user.validatePassword(password);
    if (!isValidPassword) {
      return res.status(401).json({
        error: 'Неверный email или пароль'
      });
    }

    // Проверка активности аккаунта
    if (!user.is_active) {
      return res.status(403).json({
        error: 'Аккаунт деактивирован'
      });
    }

    // Генерация токена
    const token = generateToken(user.id);

    res.json({
      message: 'Вход выполнен успешно',
      token,
      user: user.toJSON()
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      error: 'Ошибка при входе'
    });
  }
});

// GET /api/auth/me - Получение текущего пользователя
router.get('/me', authenticateToken, async (req, res) => {
  res.json({
    user: req.user.toJSON()
  });
});

// POST /api/auth/refresh - Обновление токена
router.post('/refresh', authenticateToken, async (req, res) => {
  try {
    const token = generateToken(req.user.id);
    res.json({
      token,
      user: req.user.toJSON()
    });
  } catch (error) {
    console.error('Token refresh error:', error);
    res.status(500).json({
      error: 'Ошибка при обновлении токена'
    });
  }
});

module.exports = router;
