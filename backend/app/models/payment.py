from datetime import datetime, timezone

from app import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(
        db.Integer, db.ForeignKey("purchases.id"), nullable=False
    )
    payment_system = db.Column(db.String(50), nullable=False)
    transaction_id = db.Column(db.String(255), unique=True, nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="pending")
    payment_url = db.Column(db.Text, nullable=True)
    callback_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "purchase_id": self.purchase_id,
            "payment_system": self.payment_system,
            "transaction_id": self.transaction_id,
            "amount": self.amount,
            "status": self.status,
            "payment_url": self.payment_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
