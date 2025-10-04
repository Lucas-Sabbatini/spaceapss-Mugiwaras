# Quick Start Guide

## 1. Instalar Dependências

```powershell
# Instalar pacote em modo editable
pip install -e ".[dev]"
```

## 2. Configurar Ambiente

```powershell
# Copiar .env.example para .env
copy .env.example .env

# Editar .env e adicionar sua OPENAI_API_KEY
notepad .env
```

## 3. Subir Redis Stack

```powershell
docker compose up -d
```

Aguarde alguns segundos e acesse Redis Insight em http://localhost:8001

## 4. Ingerir Dados

```powershell
# Carregar artigos no Redis
python -m packages.ingest.app.load_json

# Gerar embeddings
python -m packages.ingest.app.make_embeddings
```

## 5. Iniciar API

```powershell
uvicorn packages.api.app.main:app --reload --port 8000
```

Acesse http://localhost:8000/docs para ver a documentação interativa.

## 6. Testar

```powershell
# Health check
curl http://localhost:8000/health

# Fazer uma pergunta
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"question\":\"Quais efeitos da microgravidade em células-tronco?\",\"topK\":5}"
```

## Comandos Úteis

```powershell
# Rodar testes
pytest

# Formatar código
black packages/

# Lint
ruff check packages/

# Parar Redis
docker compose down
```

## Troubleshooting

### Redis não conecta
- Verifique se Docker está rodando: `docker ps`
- Reinicie o container: `docker compose restart`

### Erro ao gerar embeddings
- Verifique se OPENAI_API_KEY está configurado no .env
- Teste a chave: https://platform.openai.com/api-keys

### API não inicia
- Verifique se porta 8000 está livre: `netstat -an | findstr 8000`
- Tente outra porta: `uvicorn packages.api.app.main:app --port 8001`

### Modo Fallback (sem Redis)
O sistema funciona mesmo sem Redis conectado, carregando samples em memória!
