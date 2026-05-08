#!/bin/bash

# Скрипт для мониторинга синхронизации документов

echo "📊 Мониторинг синхронизации AI backend"
echo "========================================"
echo ""

while true; do
    # Очистка экрана
    clear

    echo "📊 Мониторинг синхронизации AI backend"
    echo "========================================"
    echo "⏱ $(date '+%H:%M:%S')"
    echo ""

    # Статистика из Django
    echo "🤖 Django AI Backend:"
    docker compose exec -T ai-backend python manage.py shell 2>/dev/null <<'EOF'
from app_shnq.models import Document, Clause, ClauseEmbedding
docs = Document.objects.count()
clauses = Clause.objects.count()
embeddings = ClauseEmbedding.objects.count()
print(f"   📄 Documents: {docs}")
print(f"   📝 Clauses: {clauses}")
print(f"   🧠 Embeddings: {embeddings}")
if clauses > 0:
    coverage = round(embeddings / clauses * 100)
    print(f"   📊 Coverage: {coverage}%")
EOF

    echo ""
    echo "📋 Flask Backend:"
    docker compose exec -T backend python -c "
from app import create_app
from app.models.document import Document
app = create_app()
with app.app_context():
    print(f'   📄 Total documents: {Document.query.count()}')
" 2>/dev/null

    echo ""
    echo "📝 Последние логи Django (PDF parsing):"
    docker compose logs ai-backend --tail=5 2>/dev/null | grep -E "\[clauses|Created|POST /api/sync" | tail -3

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Обновление каждые 10 секунд... (Ctrl+C для выхода)"

    sleep 10
done
