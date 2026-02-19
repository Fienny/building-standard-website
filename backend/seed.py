"""Seed the database with initial documents and an admin user."""

from app import create_app, db
from app.models.user import User
from app.models.document import Document

DOCUMENTS = [
    {
        "title": "ОзДСт 2710:2019 Строительство. Правила приемки работ",
        "category": "Строительство",
        "year": 2019,
        "pages": 15,
        "description": "Стандарт устанавливает правила приемки строительных работ.",
    },
    {
        "title": "ОзДСт 8.417:2002 Единицы величин",
        "category": "Метрология",
        "year": 2002,
        "pages": 28,
        "description": "Настоящий стандарт устанавливает единицы физических величин.",
    },
    {
        "title": "ОзДСт 2.105:2020 Общие требования к текстовым документам",
        "category": "Документация",
        "year": 2020,
        "pages": 32,
        "description": "Стандарт устанавливает общие требования к текстовым документам.",
    },
    {
        "title": "ОзДСт 21.101:2021 Основные требования к проектной документации",
        "category": "Проектирование",
        "year": 2021,
        "pages": 45,
        "description": "Стандарт устанавливает основные требования к проектной документации.",
    },
    {
        "title": "ОзДСт 12.0.003:2018 Опасные и вредные производственные факторы",
        "category": "Безопасность труда",
        "year": 2018,
        "pages": 52,
        "description": "Стандарт устанавливает классификацию опасных производственных факторов.",
    },
    {
        "title": "ОзДСт 34.602:2019 Техническое задание. Требования к содержанию",
        "category": "ИТ и автоматизация",
        "year": 2019,
        "pages": 18,
        "description": "Стандарт устанавливает требования к содержанию ТЗ.",
    },
    {
        "title": "ОзДСт 30494:2017 Здания жилые и общественные. Параметры микроклимата",
        "category": "Строительство",
        "year": 2017,
        "pages": 24,
        "description": "Стандарт устанавливает параметры микроклимата в помещениях.",
    },
    {
        "title": "ОзДСт 12.1.003:2020 Шум. Общие требования безопасности",
        "category": "Безопасность труда",
        "year": 2020,
        "pages": 20,
        "description": "Стандарт устанавливает общие требования по защите от шума.",
    },
    {
        "title": "ОзДСт 2.301:2018 Форматы чертежей",
        "category": "Документация",
        "year": 2018,
        "pages": 8,
        "description": "Стандарт устанавливает форматы листов чертежей.",
    },
    {
        "title": "ОзДСт 15467:2021 Управление качеством продукции",
        "category": "Менеджмент качества",
        "year": 2021,
        "pages": 16,
        "description": "Стандарт устанавливает основные понятия управления качеством.",
    },
]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Admin user
        if not User.query.filter_by(email="admin@standards.uz").first():
            admin = User(email="admin@standards.uz", name="Администратор", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            print("+ Создан администратор: admin@standards.uz / admin123")

        # Documents
        for d in DOCUMENTS:
            exists = Document.query.filter_by(title=d["title"]).first()
            if not exists:
                db.session.add(Document(**d))
                print(f"+ Документ: {d['title']}")

        db.session.commit()
        print("\nГотово! Seed завершен.")


if __name__ == "__main__":
    seed()
