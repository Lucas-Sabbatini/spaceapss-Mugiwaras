# Rodando localmente (Agents)

Passos mínimos para executar a API localmente conectando ao OpenAI e ao Redis remoto:

1) Ative o virtualenv

```bash
source .venv/bin/activate
```

2) Configure a variável de ambiente `OPENAI_API_KEY` em `.env` (já adicionada neste repositório como placeholder).

3) Conecte-se ao Redis remoto (opcional, a API cai em modo FALLBACK se não houver conexão):

```bash
redis-cli -u "redis://default:tIhbvHPOvH7Xap8tnVKBdnnKVpkjLAjG@redis-18380.c56.east-us.azure.redns.redis-cloud.com:18380"
```

4) Inicie a API (usando o uvicorn do venv):

```bash
.venv/bin/uvicorn packages.api.app.main:app --reload --port 8000
```

5) Teste o health endpoint:

```bash
curl http://localhost:8000/health
```

6) Fazer uma pergunta (exemplo):

```bash
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" \
  -d '{"question":"Quais efeitos da microgravidade em células-tronco?","topK":5}'
```

Observações:
- Se preferir, substitua `OPENAI_API_KEY` com uma chave real. A API usa os settings de `packages/api/app/config.py`.
- Testes unitários foram executados localmente com `pytest -q` e passaram.
