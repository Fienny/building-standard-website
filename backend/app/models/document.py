from datetime import datetime, timezone

from flask import current_app

from app import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))  # path to PDF/Word on QNAP
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    purchases = db.relationship("Purchase", backref="document", lazy="dynamic")

    @property
    def price(self):
        """Price = pages * PRICE_PER_PAGE (1000 sum per page)."""
        per_page = current_app.config.get("PRICE_PER_PAGE", 1000)
        return self.pages * per_page

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "year": self.year,
            "pages": self.pages,
            "price": self.price,
            "description": self.description,
            "file_path": self.file_path,
            "is_active": self.is_active,
        }
