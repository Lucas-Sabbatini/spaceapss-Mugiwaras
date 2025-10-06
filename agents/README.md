# SpaceAPSS Agents 🚀

Sistema de agentes inteligentes para busca e resposta sobre artigos científicos relacionados a pesquisas espaciais usando RAG (Retrieval-Augmented Generation).

## 📋 Visão Geral

O SpaceAPSS Agents é uma aplicação backend construída com FastAPI que utiliza:
- **Azure Cosmos DB (SQL API)** como banco de dados NoSQL com suporte a vector search
- **Google Gemini 2.0 Flash** como modelo de linguagem para geração de respostas
- **Text Embedding 004** para geração de embeddings vetoriais (768 dimensões)
- **Python Azure SDK** para integração com Azure Cosmos DB
- **RAG Pipeline** para gerar respostas contextualizadas baseadas em artigos científicos
- **React Markdown** no frontend para renderização de respostas formatadas

## 🏗️ Estrutura do Projeto

```
agents/
├── extract/                    # Módulos de extração de artigos
│   ├── extractor.py           # Extração de conteúdo de URLs
│   ├── fetchers.py            # Busca de documentos
│   ├── ncbi_fetcher.py        # Integração com NCBI/PubMed
│   ├── sectionizer.py         # Segmentação de documentos
│   └── enrichment_pipeline.py # Pipeline de enriquecimento com embeddings
├── packages/api/app/          # Aplicação FastAPI
│   ├── agent/                 # Pipeline do agente RAG
│   │   ├── pipeline.py        # Orquestração do pipeline
│   │   ├── prompts.py         # Templates de prompts com Markdown
│   │   └── retriever.py       # Sistema de recuperação semântica
│   ├── routers/               # Endpoints da API
│   │   ├── articles.py        # Rotas de artigos (GET /article/{id})
│   │   ├── chat.py            # Rotas de chat (POST /chat)
│   │   └── health.py          # Health checks (GET /health)
│   ├── services/              # Serviços auxiliares
│   │   ├── logger.py          # Sistema de logging estruturado
│   │   └── cosmos_data.py     # Gerenciador Azure Cosmos DB
│   ├── config.py              # Configurações da aplicação
│   ├── deps.py                # Dependências e injeção
│   ├── main.py                # Aplicação principal FastAPI
│   └── schemas.py             # Modelos Pydantic (validação)
├── shared/                    # Dados compartilhados
│   ├── SB_publication_PMC.csv            # Base de artigos PMC
│   ├── extracted_data.jsonl              # Dados extraídos (legado)
│   └── extracted_data_with_embeddings.jsonl  # Dados com embeddings
├── process_with_embeddings.py # Script de processamento em lote
├── test_vector_search.py      # Testes de busca vetorial
└── pyproject.toml             # Configuração do projeto Python
```

## 🚀 Como Rodar

### Pré-requisitos

- Python 3.11+ (recomendado Python 3.12)
- Azure Cosmos DB account (ou criar uma conta gratuita)
- Chave de API do Google Gemini (Google AI Studio)

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
# Instalar dependências básicas
pip install -r ../requirements.txt

# Instalar o projeto em modo desenvolvimento
pip install -e .

# Instalar dependências de desenvolvimento (opcional)
pip install -e ".[dev]"
```

### 3. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na pasta `agents/` com as seguintes variáveis:

```bash
# Google AI
GOOGLE_API_KEY=sua_chave_api_aqui
GOOGLE_EMBED_MODEL=models/text-embedding-004
GOOGLE_CHAT_MODEL=gemini-2.0-flash-exp

# Azure Cosmos DB
COSMOS_ENDPOINT=https://seu-cosmos-account.documents.azure.com:443/
COSMOS_KEY=sua_chave_primaria_aqui
COSMOS_DATABASE=cosmos27818-db
COSMOS_CONTAINER=cosmos27818-container

# API Configuration
API_PORT=8000
ENV=dev

# CORS (frontend)
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

**Obter credenciais:**
- **Google API Key**: https://aistudio.google.com/app/apikey
- **Azure Cosmos DB**: Portal Azure > Cosmos DB > Keys

### 4. Processar Base de Artigos (Primeira Execução)

Antes de iniciar a API, processe a base de artigos científicos:

```bash
python process_with_embeddings.py
```

Este script:
- Lê o CSV com links de artigos (`shared/SB_publication_PMC.csv`)
- Extrai conteúdo via NCBI E-utilities API
- Gera embeddings com Google Text Embedding 004 (768 dimensões)
- Armazena no Azure Cosmos DB com vector index
- Salva backup em JSONL com embeddings

**Tempo estimado:** ~30-60 minutos dependendo da quantidade de artigos e conexão

**Progresso:**
- O script mostra progresso em tempo real
- Artigos processados: X/596
- Embeddings gerados e armazenados no Cosmos DB

### 5. Iniciar a API

```bash
# Desenvolvimento (com hot reload)
python3 -m uvicorn packages.api.app.main:app --reload --host 0.0.0.0 --port 8000

# Produção
python3 -m uvicorn packages.api.app.main:app --host 0.0.0.0 --port 8000 --workers 4
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
GET /article/{experiment_id}

# Exemplo
GET /article/article-1
GET /article/article-90
```

**Resposta:**
```json
{
  "experiment_id": "article-1",
  "title": "Mice in Bion-M 1 space mission: training and selection",
  "abstract": "After a 16-year hiatus, Russia resumed...",
  "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/",
  "full_text": "Complete article text...",
  "authors": [],
  "year": null
}
```

## 🧪 Testes

```bash
# Testar busca vetorial no Cosmos DB
python test_vector_search.py

# Verificar saúde da API
curl http://localhost:8000/health

# Testar endpoint de chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the effects of microgravity on human cells?",
    "top_k": 5
  }'

# Buscar artigo específico
curl http://localhost:8000/article/article-1
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

1. **Retrieval:** Busca semântica no Azure Cosmos DB usando vector search com embeddings
2. **Ranking:** Ordena documentos por similaridade cosine (score normalizado 0-1)
3. **Synthesis:** Gera resposta em inglês usando Google Gemini 2.0 Flash com contexto recuperado
4. **Formatting:** Resposta estruturada em Markdown com bold, listas, quotes, etc.
5. **Fallback:** Responde de forma educada quando não encontra artigos relevantes

**Prompt Engineering:**
- Instruções para respostas em inglês
- Diretrizes de formatação Markdown
- Estruturação lógica (sections, bullet points)
- Citação obrigatória de fontes
- Transparência sobre limitações

## 📊 Banco de Dados

### Azure Cosmos DB (SQL API)

**Configuração:**
- **Account**: Criado via Azure Portal
- **Database**: `cosmos27818-db`
- **Container**: `cosmos27818-container`
- **Partition Key**: `/experiment_id`
- **RU/s**: 400 (shared throughput - desenvolvimento)

**Vector Search:**
- **Embedding Dimensions**: 768 (Google Text Embedding 004)
- **Similarity Metric**: Cosine similarity
- **Index Type**: Vector index configurado no container
- **Query**: `VectorDistance()` function para busca semântica

**Estrutura do Documento:**
```json
{
  "id": "article-1",
  "experiment_id": "article-1",
  "title": "Article Title",
  "abstract": "Abstract text...",
  "full_text": "Complete article...",
  "url": "https://www.ncbi.nlm.nih.gov/pmc/...",
  "embedding": [0.123, -0.456, ...],  // 768 dimensões
  "authors": [],
  "year": 2013
}
```

**Performance:**
- Latência: ~200-400ms para queries vetoriais
- Throughput: Configurável via RU/s
- Escalabilidade: Automática horizontal partition

## 🔑 Variáveis de Ambiente

| Variável | Descrição | Padrão | Obrigatório |
|----------|-----------|--------|-------------|
| `GOOGLE_API_KEY` | Chave API do Google Gemini | - | ✅ |
| `GOOGLE_EMBED_MODEL` | Modelo de embedding | `models/text-embedding-004` | ✅ |
| `GOOGLE_CHAT_MODEL` | Modelo de chat | `gemini-2.0-flash-exp` | ✅ |
| `COSMOS_ENDPOINT` | Endpoint do Azure Cosmos DB | - | ✅ |
| `COSMOS_KEY` | Chave primária do Cosmos DB | - | ✅ |
| `COSMOS_DATABASE` | Nome do database | `cosmos27818-db` | ✅ |
| `COSMOS_CONTAINER` | Nome do container | `cosmos27818-container` | ✅ |
| `API_PORT` | Porta da API | `8000` | ❌ |
| `ENV` | Ambiente (dev/prod) | `dev` | ❌ |
| `CORS_ORIGINS` | Origens permitidas CORS | `http://localhost:5173` | ❌ |

**Notas:**
- Azure Cosmos DB é obrigatório para funcionamento completo
- Sem Cosmos DB configurado, a API iniciará mas retornará resultados vazios
- Google API Key pode ser obtida em: https://aistudio.google.com/app/apikey
- Cosmos DB pode ser criado gratuitamente no Azure Portal (tier gratuito disponível)

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

### Erro: "Azure Cosmos DB connection failed"

```bash
# Verificar variáveis de ambiente
cat .env | grep COSMOS

# Testar conexão
python test_vector_search.py

# Verificar credenciais no Azure Portal
# Portal Azure > Cosmos DB Account > Keys
```

### Erro: "Google API Key not found"

Verifique se o arquivo `.env` existe e contém `GOOGLE_API_KEY`:

```bash
# Verificar .env
cat .env | grep GOOGLE_API_KEY

# Ou criar novo
echo "GOOGLE_API_KEY=sua_chave_aqui" >> .env
```

### Erro: "No documents found" / Resultados vazios

```bash
# Verificar se o Cosmos DB foi populado
python test_vector_search.py

# Se necessário, reprocessar artigos
python process_with_embeddings.py
```

### API não inicia / Porta em uso

```bash
# Verificar processos na porta 8000
lsof -i :8000  # Linux/macOS
# ou
netstat -ano | findstr :8000  # Windows

# Matar processo
kill -9 <PID>

# Ou usar outra porta
python3 -m uvicorn packages.api.app.main:app --port 8001
```

### Frontend não conecta com API

```bash
# Verificar CORS no .env
cat .env | grep CORS_ORIGINS

# Adicionar origem do frontend
CORS_ORIGINS=http://localhost:5173,http://localhost:5174

# Reiniciar API
```

## 📚 Recursos Adicionais

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure Cosmos DB for NoSQL](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/)
- [Vector Search in Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/vector-search)
- [Google Gemini API](https://ai.google.dev/docs)
- [Google AI Studio](https://aistudio.google.com/)
- [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [React Markdown](https://github.com/remarkjs/react-markdown)
- [Remark GFM](https://github.com/remarkjs/remark-gfm)

## 👥 Contribuindo

1. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
2. Commit suas mudanças (`git commit -m 'Add nova feature'`)
3. Push para a branch (`git push origin feature/nova-feature`)
4. Abra um Pull Request

## 📄 Licença

MIT

---

**SpaceAPSS Team** - Pesquisa Espacial com Inteligência Artificial 🌌
