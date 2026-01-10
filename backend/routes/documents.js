const express = require('express');
const router = express.Router();
const { Op } = require('sequelize');
const { Document, Purchase } = require('../models');
const { authenticateToken, optionalAuth, requireAdmin } = require('../middleware/auth');

// GET /api/documents - Получить список документов
router.get('/', optionalAuth, async (req, res) => {
  try {
    const { category, search, page = 1, limit = 20 } = req.query;

    const where = { is_active: true };

    // Фильтрация по категории
    if (category && category !== 'all') {
      where.category = category;
    }

    // Поиск по названию
    if (search) {
      where.title = {
        [Op.iLike]: `%${search}%`
      };
    }

    const offset = (page - 1) * limit;

    const { count, rows: documents } = await Document.findAndCountAll({
      where,
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['created_at', 'DESC']]
    });

    res.json({
      documents,
      pagination: {
        total: count,
        page: parseInt(page),
        limit: parseInt(limit),
        totalPages: Math.ceil(count / limit)
      }
    });
  } catch (error) {
    console.error('Get documents error:', error);
    res.status(500).json({
      error: 'Ошибка при получении документов'
    });
  }
});

// GET /api/documents/categories - Получить список категорий
router.get('/categories', async (req, res) => {
  try {
    const categories = await Document.findAll({
      attributes: ['category'],
      where: { is_active: true },
      group: ['category'],
      raw: true
    });

    res.json({
      categories: categories.map(c => c.category)
    });
  } catch (error) {
    console.error('Get categories error:', error);
    res.status(500).json({
      error: 'Ошибка при получении категорий'
    });
  }
});

// GET /api/documents/:id - Получить документ по ID
router.get('/:id', optionalAuth, async (req, res) => {
  try {
    const { id } = req.params;

    const document = await Document.findByPk(id);

    if (!document) {
      return res.status(404).json({
        error: 'Документ не найден'
      });
    }

    if (!document.is_active) {
      return res.status(404).json({
        error: 'Документ недоступен'
      });
    }

    // Проверка, купил ли пользователь этот документ
    let isPurchased = false;
    if (req.user) {
      const purchase = await Purchase.findOne({
        where: {
          user_id: req.user.id,
          document_id: id,
          payment_status: 'completed'
        }
      });
      isPurchased = !!purchase;
    }

    res.json({
      document: document.toJSON(),
      isPurchased
    });
  } catch (error) {
    console.error('Get document error:', error);
    res.status(500).json({
      error: 'Ошибка при получении документа'
    });
  }
});

// GET /api/documents/:id/download - Скачать документ
router.get('/:id/download', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;

    const document = await Document.findByPk(id);

    if (!document) {
      return res.status(404).json({
        error: 'Документ не найден'
      });
    }

    // Проверка покупки
    const purchase = await Purchase.findOne({
      where: {
        user_id: req.user.id,
        document_id: id,
        payment_status: 'completed'
      }
    });

    if (!purchase && req.user.role !== 'admin') {
      return res.status(403).json({
        error: 'Документ не куплен. Необходимо совершить покупку'
      });
    }

    if (!document.file_path) {
      return res.status(404).json({
        error: 'Файл документа не найден'
      });
    }

    // Увеличиваем счетчик скачиваний
    await document.increment('download_count');

    // TODO: Реализовать отправку файла
    // res.download(document.file_path);

    res.json({
      message: 'Функция скачивания будет реализована',
      downloadUrl: `/uploads/documents/${document.file_path}`
    });
  } catch (error) {
    console.error('Download document error:', error);
    res.status(500).json({
      error: 'Ошибка при скачивании документа'
    });
  }
});

// POST /api/documents - Создать документ (только для админов)
router.post('/', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const { title, category, year, pages, price, description } = req.body;

    const document = await Document.create({
      title,
      category,
      year,
      pages,
      price,
      description
    });

    res.status(201).json({
      message: 'Документ создан успешно',
      document: document.toJSON()
    });
  } catch (error) {
    console.error('Create document error:', error);
    res.status(500).json({
      error: 'Ошибка при создании документа'
    });
  }
});

// PUT /api/documents/:id - Обновить документ (только для админов)
router.put('/:id', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;

    const document = await Document.findByPk(id);

    if (!document) {
      return res.status(404).json({
        error: 'Документ не найден'
      });
    }

    await document.update(updates);

    res.json({
      message: 'Документ обновлен успешно',
      document: document.toJSON()
    });
  } catch (error) {
    console.error('Update document error:', error);
    res.status(500).json({
      error: 'Ошибка при обновлении документа'
    });
  }
});

// DELETE /api/documents/:id - Удалить документ (только для админов)
router.delete('/:id', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const { id } = req.params;

    const document = await Document.findByPk(id);

    if (!document) {
      return res.status(404).json({
        error: 'Документ не найден'
      });
    }

    // Мягкое удаление
    await document.update({ is_active: false });

    res.json({
      message: 'Документ удален успешно'
    });
  } catch (error) {
    console.error('Delete document error:', error);
    res.status(500).json({
      error: 'Ошибка при удалении документа'
    });
  }
});

module.exports = router;
