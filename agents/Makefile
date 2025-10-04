.PHONY: help deps up down dev ingest embed test format lint clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make deps     - Instalar dependências"
	@echo "  make up       - Subir Redis Stack"
	@echo "  make down     - Parar Redis Stack"
	@echo "  make dev      - Rodar API em modo dev"
	@echo "  make ingest   - Ingerir samples no Redis"
	@echo "  make embed    - Gerar embeddings"
	@echo "  make test     - Rodar testes"
	@echo "  make format   - Formatar código (black)"
	@echo "  make lint     - Lint (ruff)"
	@echo "  make clean    - Limpar cache e builds"

deps:
	pip install -e ".[dev]"

up:
	docker compose up -d
	@echo "Aguardando Redis Stack inicializar..."
	@timeout /t 5 /nobreak >nul
	@echo "Redis Stack disponível em:"
	@echo "  Redis: localhost:6379"
	@echo "  Redis Insight: http://localhost:8001"

down:
	docker compose down

dev:
	uvicorn packages.api.app.main:app --reload --port 8000

ingest:
	python -m packages.ingest.app.load_json

embed:
	python -m packages.ingest.app.make_embeddings

test:
	pytest -v

format:
	black packages/

lint:
	ruff check packages/

clean:
	@if exist "build" rmdir /s /q build
	@if exist "dist" rmdir /s /q dist
	@if exist "*.egg-info" rmdir /s /q *.egg-info
	@for /r %%i in (__pycache__) do @if exist "%%i" rmdir /s /q "%%i"
	@for /r %%i in (*.pyc) do @if exist "%%i" del /q "%%i"
	@for /r %%i in (.pytest_cache) do @if exist "%%i" rmdir /s /q "%%i"
	@echo "Limpeza concluída!"
