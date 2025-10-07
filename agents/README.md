# SpaceAPSS Agents 🚀

Sistema de agentes inteligentes para busca e resposta sobre artigos científicos relacionados a pesquisas espaciais usando RAG (Retrieval-Augmented Generation).

## 📋 Visão Geral

O SpaceAPSS Agents é uma aplicação backend construída com FastAPI que utiliza:
- **ChromaDB** como banco de dados vetorial para armazenamento e busca semântica
- **Google Gemini** (gemini-2.0-flash) como modelo de linguagem
- **Text Embedding 004** para embeddings de documentos
- **Redis** para cache e gerenciamento de sessões
- **RAG Pipeline** para gerar respostas contextualizadas baseadas em artigos científicos

## 🏗️ Estrutura do Projeto

```
agents/
├── extract/                    # Módulos de extração de artigos
│   ├── extractor.py           # Extração de conteúdo de URLs
│   ├── fetchers.py            # Busca de documentos
│   ├── ncbi_fetcher.py        # Integração com NCBI/PubMed
│   └── sectionizer.py         # Segmentação de documentos
├── packages/api/app/          # Aplicação FastAPI
│   ├── agent/                 # Pipeline do agente RAG
│   │   ├── pipeline.py        # Orquestração do pipeline
│   │   ├── prompts.py         # Templates de prompts
│   │   └── retriever.py       # Sistema de recuperação
│   ├── routers/               # Endpoints da API
│   │   ├── articles.py        # Rotas de artigos
│   │   ├── chat.py            # Rotas de chat
│   │   └── health.py          # Health checks
│   ├── services/              # Serviços auxiliares
│   │   ├── logger.py          # Sistema de logging
│   │   └── vector_db.py       # Gerenciador ChromaDB
│   ├── config.py              # Configurações
│   ├── deps.py                # Dependências
│   ├── main.py                # Aplicação principal
│   └── schemas.py             # Modelos Pydantic
├── shared/                    # Dados compartilhados
│   ├── SB_publication_PMC.csv # Base de artigos
│   └── extracted_data.jsonl   # Dados extraídos
├── chroma_db/                 # Banco de dados vetorial
├── proccess_batch.py          # Script de processamento em lote
├── test_integration.py        # Testes de integração
└── pyproject.toml             # Configuração do projeto
```

## 🚀 Como Rodar

### Pré-requisitos

- Python 3.11+
- Redis (local ou cloud)
- Chave de API do Google Gemini

### 1. Configurar Ambiente Virtual

```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate     # Windows
```

### 2. Instalar Dependências

```bash
# Instalar o projeto com todas as dependências
pip install -e .

# OU instalar com dependências de desenvolvimento
pip install -e ".[dev]"
```

### 3. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na pasta `agents/` com as seguintes variáveis:

```bash
# Google Gemini
GOOGLE_API_KEY=sua_chave_api_aqui
GOOGLE_EMBED_MODEL=models/text-embedding-004
GOOGLE_CHAT_MODEL=gemini-2.0-flash

# Redis
REDIS_URL=redis://localhost:6379
REDIS_USERNAME=default
REDIS_PASSWORD=sua_senha_aqui

# API
API_PORT=8000
ENV=dev

# CORS (frontend)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 4. Processar Base de Artigos (Primeira Execução)

Antes de iniciar a API, processe a base de artigos científicos:

```bash
python proccess_batch.py
```

Este script:
- Lê o CSV com links de artigos (`shared/SB_publication_PMC.csv`)
- Extrai conteúdo via NCBI API
- Gera embeddings e armazena no ChromaDB
- Salva backup em JSONL

**Tempo estimado:** ~30-60 minutos dependendo da quantidade de artigos

### 5. Iniciar a API

```bash
uvicorn packages.api.app.main:app --reload --port 8000
```

A API estará disponível em: `http://localhost:8000`

### 6. Acessar Documentação

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📡 Endpoints Principais

### Health Check
```http
GET /health
```

### Chat com o Agente
```http
POST /chat
Content-Type: application/json

{
  "question": "Quais são os efeitos da microgravidade em células humanas?",
  "top_k": 5
}
```

### Listar Artigos
```http
GET /articles?limit=10&offset=0
```

### Buscar Artigo por ID
```http
GET /articles/{article_id}
```

## 🧪 Testes

```bash
# Executar testes de integração
pytest test_integration.py -v

# Com cobertura
pytest test_integration.py --cov=packages --cov-report=html
```

## 🔧 Desenvolvimento

### Formatação de Código

```bash
# Formatar com black
black packages/ extract/

# Lint com ruff
ruff check packages/ extract/
```

### Estrutura do Pipeline RAG

1. **Retrieval:** Busca semântica no ChromaDB usando embeddings
2. **Ranking:** Ordena documentos por relevância
3. **Synthesis:** Gera resposta usando Google Gemini com contexto recuperado
4. **Fallback:** Responde sem contexto se não encontrar artigos relevantes

## 📊 Banco de Dados Vetorial

O ChromaDB é inicializado automaticamente em `chroma_db/` e persiste os dados localmente. Não é necessário configuração adicional.

**Coleção:** `nasa_space_collection`

## 🔑 Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `GOOGLE_API_KEY` | Chave API do Google Gemini | - |
| `GOOGLE_EMBED_MODEL` | Modelo de embedding | `models/text-embedding-004` |
| `GOOGLE_CHAT_MODEL` | Modelo de chat | `gemini-2.0-flash` |
| `REDIS_URL` | URL de conexão Redis | `redis://localhost:6379` |
| `API_PORT` | Porta da API | `8000` |
| `ENV` | Ambiente (dev/prod) | `dev` |
| `CORS_ORIGINS` | Origens permitidas CORS | `http://localhost:5173` |

## 📝 Logs

Os logs são salvos em:
- Console (desenvolvimento)
- Arquivos em `logs/` (produção)

Níveis de log:
- `INFO`: Operações normais
- `WARNING`: Avisos
- `ERROR`: Erros
- `DEBUG`: Debugging detalhado (apenas em dev)

## 🐛 Troubleshooting

### Erro: "Permission denied (os error 13)" no ChromaDB

```bash
# Verificar permissões do diretório
chmod -R 755 chroma_db/

# Ou remover e recriar
rm -rf chroma_db/
python proccess_batch.py
```

### Erro: "Redis connection refused"

Certifique-se que o Redis está rodando:

```bash
# Iniciar Redis localmente
redis-server

# Ou usar Docker
docker run -d -p 6379:6379 redis:latest
```

### Erro: "Google API Key not found"

Verifique se o arquivo `.env` existe e contém `GOOGLE_API_KEY`.

## 📚 Recursos Adicionais

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Google Gemini API](https://ai.google.dev/docs)
- [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/)

## 👥 Contribuindo

1. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
2. Commit suas mudanças (`git commit -m 'Add nova feature'`)
3. Push para a branch (`git push origin feature/nova-feature`)
4. Abra um Pull Request

## 📄 Licença

MIT

---

**SpaceAPSS Team** - Pesquisa Espacial com Inteligência Artificial 🌌
