const express = require('express');
const router = express.Router();
const { User, Purchase, Document } = require('../models');
const { authenticateToken } = require('../middleware/auth');

// GET /api/users/profile - Получить профиль текущего пользователя
router.get('/profile', authenticateToken, async (req, res) => {
  try {
    res.json({
      user: req.user.toJSON()
    });
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({
      error: 'Ошибка при получении профиля'
    });
  }
});

// PUT /api/users/profile - Обновить профиль
router.put('/profile', authenticateToken, async (req, res) => {
  try {
    const { name, email } = req.body;

    // Проверка email на уникальность
    if (email && email !== req.user.email) {
      const existingUser = await User.findOne({ where: { email } });
      if (existingUser) {
        return res.status(400).json({
          error: 'Пользователь с таким email уже существует'
        });
      }
    }

    await req.user.update({ name, email });

    res.json({
      message: 'Профиль обновлен успешно',
      user: req.user.toJSON()
    });
  } catch (error) {
    console.error('Update profile error:', error);
    res.status(500).json({
      error: 'Ошибка при обновлении профиля'
    });
  }
});

// PUT /api/users/password - Изменить пароль
router.put('/password', authenticateToken, async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body;

    if (!currentPassword || !newPassword) {
      return res.status(400).json({
        error: 'Необходимо указать текущий и новый пароль'
      });
    }

    if (newPassword.length < 6) {
      return res.status(400).json({
        error: 'Новый пароль должен быть минимум 6 символов'
      });
    }

    // Проверка текущего пароля
    const isValidPassword = await req.user.validatePassword(currentPassword);
    if (!isValidPassword) {
      return res.status(401).json({
        error: 'Неверный текущий пароль'
      });
    }

    // Установка нового пароля
    await req.user.setPassword(newPassword);
    await req.user.save();

    res.json({
      message: 'Пароль изменен успешно'
    });
  } catch (error) {
    console.error('Change password error:', error);
    res.status(500).json({
      error: 'Ошибка при изменении пароля'
    });
  }
});

// GET /api/users/purchases - Получить купленные документы
router.get('/purchases', authenticateToken, async (req, res) => {
  try {
    const purchases = await Purchase.findAll({
      where: {
        user_id: req.user.id,
        payment_status: 'completed'
      },
      include: [{
        model: Document,
        as: 'document',
        attributes: ['id', 'title', 'category', 'year', 'pages', 'file_path', 'preview_path']
      }],
      order: [['created_at', 'DESC']]
    });

    res.json({
      purchases: purchases.map(p => ({
        purchase_id: p.id,
        purchased_at: p.created_at,
        amount: p.amount,
        document: p.document
      }))
    });
  } catch (error) {
    console.error('Get purchases error:', error);
    res.status(500).json({
      error: 'Ошибка при получении покупок'
    });
  }
});

module.exports = router;
