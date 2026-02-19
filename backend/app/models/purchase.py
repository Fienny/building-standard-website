from datetime import datetime, timezone

from app import db


class Purchase(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    document_id = db.Column(
        db.Integer, db.ForeignKey("documents.id"), nullable=False
    )
    amount = db.Column(db.Integer, nullable=False)  # price at time of purchase
    payment_method = db.Column(db.String(50), nullable=False)  # click/payme/card
    payment_status = db.Column(db.String(50), default="pending")
    transaction_id = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    payments = db.relationship("Payment", backref="purchase", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "document_id": self.document_id,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "transaction_id": self.transaction_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
