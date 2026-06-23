.PHONY: setup up down test lint migrate logs

setup:
	@echo "📦 Копируем .env из шаблона (если ещё нет)…"
	@if not exist .env copy .env.example .env
	@echo "🐳 Собираем и поднимаем контейнеры…"
	docker compose build --no-cache
	docker compose up -d postgres redis
	@echo "⏳ Ждём готовности PostgreSQL…"
	@timeout /t 8 /nobreak > nul 2>&1 || true
	@echo "🔄 Запускаем миграции…"
	docker compose run --rm api alembic upgrade head
	@echo "🚀 Поднимаем все сервисы…"
	docker compose up -d
	@echo ""
	@echo "✅ Готово!"
	@echo "   API:        http://localhost:8099/docs"
	@echo "   Flower:     http://localhost:5599"
	@echo "   Grafana:    http://localhost:3099"
	@echo "   Prometheus: http://localhost:9099"

test:
	docker compose run --rm -e APP_ENV=test api python -m pytest -v --tb=short

up:
	docker compose up -d

down:
	docker compose down

migrate:
	docker compose run --rm api alembic upgrade head

lint:
	docker compose run --rm api ruff check src/ tests/

logs:
	docker compose logs -f api worker beat
