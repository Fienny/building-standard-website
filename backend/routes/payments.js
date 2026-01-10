const express = require('express');
const router = express.Router();
const { Purchase, Payment, Document } = require('../models');
const { authenticateToken } = require('../middleware/auth');

// POST /api/payments/create - Создать платеж
router.post('/create', authenticateToken, async (req, res) => {
  try {
    const { document_id, payment_method } = req.body;

    // Валидация
    if (!document_id || !payment_method) {
      return res.status(400).json({
        error: 'Необходимо указать document_id и payment_method'
      });
    }

    if (!['click', 'payme', 'card'].includes(payment_method)) {
      return res.status(400).json({
        error: 'Неверный метод оплаты'
      });
    }

    // Проверка документа
    const document = await Document.findByPk(document_id);
    if (!document || !document.is_active) {
      return res.status(404).json({
        error: 'Документ не найден'
      });
    }

    // Проверка, не купил ли уже пользователь
    const existingPurchase = await Purchase.findOne({
      where: {
        user_id: req.user.id,
        document_id,
        payment_status: 'completed'
      }
    });

    if (existingPurchase) {
      return res.status(400).json({
        error: 'Вы уже приобрели этот документ'
      });
    }

    // Создание покупки
    const purchase = await Purchase.create({
      user_id: req.user.id,
      document_id,
      amount: document.price,
      payment_method,
      payment_status: 'pending'
    });

    // Создание платежа
    const payment = await Payment.create({
      purchase_id: purchase.id,
      payment_system: payment_method,
      amount: document.price,
      status: 'pending'
    });

    // TODO: Здесь будет интеграция с платежными системами
    // В зависимости от payment_method вызываем соответствующий сервис
    let paymentUrl = null;

    switch (payment_method) {
      case 'click':
        // paymentUrl = await clickService.createPayment(payment);
        paymentUrl = 'https://my.click.uz/services/pay?service_id=XXXXX&amount=' + document.price;
        break;
      case 'payme':
        // paymentUrl = await paymeService.createPayment(payment);
        paymentUrl = 'https://checkout.paycom.uz/XXXXX';
        break;
      case 'card':
        // paymentUrl = await cardService.createPayment(payment);
        paymentUrl = 'https://payment-gateway.uz/pay';
        break;
    }

    // Обновляем payment_url
    await payment.update({ payment_url: paymentUrl });

    res.status(201).json({
      message: 'Платеж создан успешно',
      purchase_id: purchase.id,
      payment_id: payment.id,
      payment_url: paymentUrl,
      amount: document.price
    });
  } catch (error) {
    console.error('Create payment error:', error);
    res.status(500).json({
      error: 'Ошибка при создании платежа'
    });
  }
});

// POST /api/payments/callback/:system - Webhook от платежных систем
router.post('/callback/:system', async (req, res) => {
  try {
    const { system } = req.params;
    const callbackData = req.body;

    console.log(`Received callback from ${system}:`, callbackData);

    // TODO: Реализовать обработку callback'ов для каждой платежной системы
    // Каждая система имеет свой формат данных и требует проверки подписи

    switch (system) {
      case 'click':
        // await clickService.handleCallback(callbackData);
        break;
      case 'payme':
        // await paymeService.handleCallback(callbackData);
        break;
      case 'card':
        // await cardService.handleCallback(callbackData);
        break;
      default:
        return res.status(400).json({ error: 'Unknown payment system' });
    }

    res.json({ success: true });
  } catch (error) {
    console.error('Payment callback error:', error);
    res.status(500).json({
      error: 'Ошибка при обработке callback'
    });
  }
});

// GET /api/payments/status/:id - Проверить статус платежа
router.get('/status/:id', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;

    const payment = await Payment.findByPk(id, {
      include: [{
        model: Purchase,
        as: 'purchase',
        where: { user_id: req.user.id }
      }]
    });

    if (!payment) {
      return res.status(404).json({
        error: 'Платеж не найден'
      });
    }

    res.json({
      payment_id: payment.id,
      status: payment.status,
      amount: payment.amount,
      payment_system: payment.payment_system,
      created_at: payment.created_at
    });
  } catch (error) {
    console.error('Get payment status error:', error);
    res.status(500).json({
      error: 'Ошибка при получении статуса платежа'
    });
  }
});

// GET /api/payments/history - История платежей пользователя
router.get('/history', authenticateToken, async (req, res) => {
  try {
    const { page = 1, limit = 20 } = req.query;
    const offset = (page - 1) * limit;

    const { count, rows: purchases } = await Purchase.findAndCountAll({
      where: { user_id: req.user.id },
      include: [
        {
          model: Document,
          as: 'document',
          attributes: ['id', 'title', 'category', 'year']
        },
        {
          model: Payment,
          as: 'payments',
          attributes: ['id', 'status', 'payment_system', 'created_at']
        }
      ],
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['created_at', 'DESC']]
    });

    res.json({
      purchases,
      pagination: {
        total: count,
        page: parseInt(page),
        limit: parseInt(limit),
        totalPages: Math.ceil(count / limit)
      }
    });
  } catch (error) {
    console.error('Get payment history error:', error);
    res.status(500).json({
      error: 'Ошибка при получении истории платежей'
    });
  }
});

module.exports = router;
