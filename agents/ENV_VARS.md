# 🔐 Variáveis de Ambiente

Este arquivo documenta todas as variáveis de ambiente suportadas pela aplicação.

## Arquivo .env

Copie `.env.example` para `.env` e preencha com seus valores:

```bash
cp .env.example .env
```

## Variáveis Obrigatórias

### LLM Provider
```bash
# Provedor de LLM: "openai" ou "azure"
PROVIDER=openai
```

### OpenAI (se PROVIDER=openai)
```bash
# Chave da API OpenAI
# Obtenha em: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Modelo de embeddings (padrão: text-embedding-3-small)
OPENAI_EMBED_MODEL=text-embedding-3-small

# Modelo de chat (padrão: gpt-4o-mini)
OPENAI_CHAT_MODEL=gpt-4o-mini
```

### Azure OpenAI (se PROVIDER=azure)
```bash
# Endpoint do Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Chave da API Azure OpenAI
AZURE_OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Nome do deployment de embeddings
AZURE_OPENAI_EMBED_DEPLOYMENT=text-embedding-3-small

# Nome do deployment de chat
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini

# Versão da API (padrão: 2024-06-01)
AZURE_OPENAI_API_VERSION=2024-06-01
```

## Variáveis Opcionais

### Redis
```bash
# URL de conexão do Redis (padrão: redis://localhost:6379)
REDIS_URL=redis://localhost:6379

# Usuário Redis (opcional, para Redis com auth)
REDIS_USERNAME=

# Senha Redis (opcional, para Redis com auth)
REDIS_PASSWORD=
```

**Nota:** Se Redis não estiver disponível, o sistema automaticamente entra em modo fallback.

### API
```bash
# Porta da API (padrão: 8000)
API_PORT=8000

# Ambiente: "dev" ou "prod" (padrão: dev)
ENV=dev
```

### CORS
```bash
# Origens permitidas para CORS (separadas por vírgula)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Exemplos de Configuração

### Desenvolvimento Local (OpenAI)
```bash
PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_EMBED_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini

REDIS_URL=redis://localhost:6379
API_PORT=8000
ENV=dev
CORS_ORIGINS=http://localhost:5173
```

### Desenvolvimento Local (Azure OpenAI)
```bash
PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://my-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AZURE_OPENAI_EMBED_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-06-01

REDIS_URL=redis://localhost:6379
API_PORT=8000
ENV=dev
CORS_ORIGINS=http://localhost:5173
```

### Produção (com Redis autenticado)
```bash
PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_EMBED_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini

REDIS_URL=redis://redis-prod.example.com:6379
REDIS_USERNAME=admin
REDIS_PASSWORD=super-secret-password

API_PORT=8000
ENV=prod
CORS_ORIGINS=https://app.example.com,https://www.example.com
```

### Modo Fallback (sem Redis)
```bash
PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_EMBED_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini

# Redis não configurado ou offline
# REDIS_URL=

API_PORT=8000
ENV=dev
CORS_ORIGINS=http://localhost:5173
```

## Modelos Suportados

### Embeddings
- `text-embedding-3-small` (1536 dims, recomendado) ⭐
- `text-embedding-3-large` (3072 dims, mais preciso mas mais caro)
- `text-embedding-ada-002` (1536 dims, legado)

**Nota:** Se mudar o modelo, ajuste a dimensão do vetor no `redis_client.py` (linha com `"DIM": 1536`).

### Chat
- `gpt-4o-mini` (rápido e econômico, recomendado) ⭐
- `gpt-4o` (mais preciso mas mais caro)
- `gpt-4-turbo` (legado)
- `gpt-3.5-turbo` (mais barato mas menos preciso)

## Segurança

### ⚠️ NUNCA commite o arquivo .env!

O `.gitignore` já está configurado para ignorar `.env`, mas sempre verifique:

```bash
# Verificar se .env está ignorado
git status

# Adicionar manualmente se necessário
echo ".env" >> .gitignore
```

### 🔒 Variáveis sensíveis

Estas variáveis contêm informações sensíveis e **nunca devem ser expostas**:
- `OPENAI_API_KEY`
- `AZURE_OPENAI_API_KEY`
- `REDIS_PASSWORD`

### 🏢 Em produção

Use serviços de gerenciamento de secrets:
- **Azure**: Azure Key Vault
- **AWS**: AWS Secrets Manager
- **GCP**: Google Secret Manager
- **Kubernetes**: Kubernetes Secrets
- **Docker**: Docker Secrets

## Validação de Variáveis

A aplicação valida variáveis na inicialização via Pydantic Settings.

### Erros comuns:

#### "OPENAI_API_KEY is required"
```bash
# Solução: adicione a chave no .env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### "Could not connect to Redis"
```bash
# Solução 1: Subir Redis
docker compose up -d

# Solução 2: Usar modo fallback (sistema funciona mesmo sem Redis!)
# Apenas comente ou remova REDIS_URL do .env
```

#### "Invalid provider"
```bash
# Solução: use "openai" ou "azure"
PROVIDER=openai
```

## Testar Configuração

```bash
# Verificar health (inclui status do Redis)
curl http://localhost:8000/health

# Testar embeddings
python -c "
from packages.api.app.services.embeddings import get_embeddings_service
emb = get_embeddings_service()
result = emb.get_embedding('test')
print(f'Embedding gerado: {len(result)} dims')
"

# Testar Redis
python -c "
from packages.api.app.services.redis_client import get_redis_client
redis = get_redis_client()
print(f'Redis conectado: {redis.is_connected()}')
"
```

## Referências

- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [OpenAI Models](https://platform.openai.com/docs/models)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
- [Redis Configuration](https://redis.io/docs/management/config/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
