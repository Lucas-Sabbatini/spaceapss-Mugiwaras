# SpaceAPSS Agents

Sistema de agentes inteligentes para análise, recuperação e visualização de artigos científicos relacionados a pesquisas espaciais utilizando RAG (Retrieval-Augmented Generation) e Knowledge Graphs.

## Visão Geral

O SpaceAPSS Agents é uma plataforma backend completa construída com FastAPI que integra:
- **MongoDB** para armazenamento de artigos enriquecidos e metadados
- **NetworkX** para construção e análise de Knowledge Graphs
- **Google Gemini** (gemini-2.0-flash-exp) como modelo de linguagem para chat
- **Text Embedding 004** para geração de embeddings de documentos
- **NCBI E-utilities API** para extração de artigos do PubMed Central
- **RAG Pipeline** para geração de respostas contextualizadas
- **Knowledge Graph** para visualização de relações entre entidades científicas

## Estrutura do Projeto

```
agents/
├── extract/                           # Módulos de extração e enriquecimento
│   ├── extractor.py                  # Extração de conteúdo de URLs
│   ├── fetchers.py                   # Busca de documentos
│   ├── ncbi_fetcher.py               # Integração com NCBI E-utilities API
│   ├── sectionizer.py                # Segmentação de documentos científicos
│   ├── enrichment_pipeline.py        # Pipeline de enriquecimento de dados
│   ├── models.py                     # Modelos de dados
│   └── function.json                 # Definições de funções para LLM
├── packages/api/app/                 # Aplicação FastAPI
│   ├── agent/                        # Pipeline do agente RAG
│   │   ├── pipeline.py              # Orquestração do pipeline
│   │   ├── prompts.py               # Templates de prompts
│   │   └── retriever.py             # Sistema de recuperação
│   ├── routers/                     # Endpoints da API
│   │   ├── articles.py              # CRUD de artigos
│   │   ├── chat.py                  # Interface de chat
│   │   ├── graph.py                 # Endpoints do Knowledge Graph
│   │   └── health.py                # Health checks
│   ├── services/                    # Serviços auxiliares
│   │   ├── graph_service.py         # Manipulação do Knowledge Graph
│   │   ├── logger.py                # Sistema de logging
│   │   └── mongo_data.py            # Gerenciador MongoDB/Cosmos DB
│   ├── config.py                    # Configurações da aplicação
│   ├── deps.py                      # Gerenciamento de dependências
│   ├── graph.py                     # Classe KnowledgeGraph
│   ├── main.py                      # Aplicação principal
│   └── schemas.py                   # Modelos Pydantic
├── graphs/                          # Grafos de conhecimento gerados
│   ├── *.gpickle                    # Formato NetworkX
│   ├── *.graphml                    # Formato GraphML
│   ├── *.json                       # Formato JSON
│   ├── *_visualization.png          # Visualizações
│   └── *_stats.txt                  # Estatísticas
├── shared/                          # Dados compartilhados
│   ├── SB_publication_PMC.csv       # Base de artigos PMC
│   └── extracted_data.jsonl         # Dados extraídos e enriquecidos
├── build_knowledge_graph.py         # Construção do Knowledge Graph
├── call_and_insert_in_DB.py        # Enriquecimento e inserção no DB
├── test_graph_visualization.py      # Testes de visualização
├── pyproject.toml                   # Configuração do projeto
├── GRAPH_VISUALIZATION.md           # Documentação de visualização
└── DISPERSAO_NOS.md                 # Documentação de dispersão de nós
```

## Como Executar

### Pré-requisitos

- Python 3.11 ou superior
- MongoDB local ou Azure Cosmos DB
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
GOOGLE_CHAT_MODEL=gemini-2.0-flash-exp

# MongoDB/Cosmos DB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=spaceapss
MONGODB_COLLECTION=articles

# Redis
REDIS_URL=redis://localhost:6379
REDIS_USERNAME=default
REDIS_PASSWORD=sua_senha_aqui

# API
API_PORT=8000
ENV=dev

# CORS (frontend)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Knowledge Graph
GRAPH_PATH=graphs/knowledge_graph_latest.gpickle
```

### 4. Processar e Enriquecer Artigos (Primeira Execução)

Execute o pipeline de enriquecimento de dados:

```bash
python call_and_insert_in_DB.py
```

Este script executa:
- Leitura do CSV com links de artigos (`shared/SB_publication_PMC.csv`)
- Extração de conteúdo via NCBI E-utilities API
- Enriquecimento com LLM (extração de entidades, objetivos, métodos, etc.)
- Armazenamento no MongoDB/Cosmos DB
- Salvamento de backup em JSONL

**Tempo estimado:** 30-120 minutos dependendo da quantidade de artigos e configuração da LLM

### 5. Construir Knowledge Graph

Após o enriquecimento, construa o grafo de conhecimento:

```bash
python build_knowledge_graph.py
```

Este script:
- Lê dados enriquecidos do MongoDB
- Extrai entidades (autores, instituições, organismos, termos MeSH, journals)
- Constrói grafo de relações usando NetworkX
- Gera visualizações e estatísticas
- Salva em múltiplos formatos (gpickle, graphml, json)

**Saída:** Arquivos no diretório `graphs/`

### 6. Iniciar a API

```bash
cd agents
uvicorn packages.api.app.main:app --reload --port 8000
```

A API estará disponível em: `http://localhost:8000`

### 7. Acessar Documentação Interativa

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Endpoints Principais

### Health Check
```http
GET /health
```

Retorna o status da API e de suas dependências (MongoDB, Redis, Knowledge Graph).

### Chat RAG

```http
POST /api/chat/query
Content-Type: application/json

{
  "message": "What are the effects of microgravity on bone density?",
  "experiment_id": "exp_001",
  "top_k": 5
}
```

Realiza consulta sobre artigos científicos usando Retrieval-Augmented Generation (RAG).

**Response:**
```json
{
  "answer": "Based on the analyzed articles...",
  "sources": [
    {
      "pmcid": "PMC1234567",
      "title": "Bone Loss in Microgravity",
      "authors": ["Smith J", "Doe A"],
      "year": 2023,
      "relevance_score": 0.92
    }
  ],
  "metadata": {
    "experiment_id": "exp_001",
    "query_time_ms": 1234
  }
}
```

### Knowledge Graph

**Obter Subgrafo de Experimento:**
```http
GET /api/graph/{experiment_id}
```

Retorna todos os nós e arestas do Knowledge Graph relacionados ao experimento.

**Expandir Vizinhos de um Nó:**
```http
GET /api/graph/neighbors/{node_id}?max_depth=1&no_experiment_id=exp_001
```

Retorna os vizinhos de um nó específico. O parâmetro `no_experiment_id` filtra nós que NÃO pertencem ao experimento especificado, permitindo expansão do grafo com entidades de outros experimentos.

**Response:**
```json
{
  "nodes": [
    {
      "id": "author_123",
      "label": "John Smith",
      "type": "author",
      "experiment_ids": ["exp_002", "exp_003"]
    }
  ],
  "edges": [...],
  "center_node_id": "author_123"
}
```

### Artigos

**Listar Artigos:**
```http
GET /api/articles?limit=10&offset=0&experiment_id=exp_001
```

**Buscar Artigo por PMCID:**
```http
GET /api/articles/{pmcid}
```

Retorna os detalhes completos incluindo seções, entidades extraídas, objetivos, métodos e resultados enriquecidos.

## Desenvolvimento

### Formatação de Código

```bash
# Formatar código com Black
black packages/ extract/

# Verificar linting com Ruff
ruff check packages/ extract/
```

### Estrutura do Pipeline RAG

1. **Retrieval:** Busca semântica no MongoDB usando embeddings e índices vetoriais
2. **Ranking:** Ordena documentos por relevância (similaridade de cosseno)
3. **Synthesis:** Gera resposta contextualizada usando Google Gemini com documentos recuperados
4. **Fallback:** Responde sem contexto quando não há artigos relevantes

### Arquitetura de Enriquecimento de Dados

O pipeline de enriquecimento (`enrichment_pipeline.py`) processa artigos em etapas:

1. **Fetch:** Download de artigos da NCBI E-utilities API
2. **Section:** Divisão em seções estruturadas (abstract, introduction, methods, etc.)
3. **Enrichment:** Extração de entidades usando LLM (Google Gemini)
   - Objetivos e hipóteses
   - Métodos e procedimentos
   - Resultados e conclusões
   - Entidades nomeadas (autores, instituições, organismos, termos MeSH)
4. **Storage:** Armazenamento no MongoDB com índices para busca eficiente

## Banco de Dados

### MongoDB / Azure Cosmos DB

Armazena artigos enriquecidos com metadados estruturados e embeddings para busca semântica.

**Coleção Principal:** `articles`

**Schema Exemplo:**
```json
{
  "pmcid": "PMC1234567",
  "title": "...",
  "authors": [...],
  "abstract": "...",
  "sections": {...},
  "enrichment": {
    "objective": "...",
    "methods": "...",
    "entities": {
      "organisms": [...],
      "institutions": [...],
      "mesh_terms": [...]
    }
  },
  "embedding": [0.123, -0.456, ...],
  "experiment_ids": ["exp_001"]
}
```

### Knowledge Graph

Representação em NetworkX armazenada em múltiplos formatos:
- **GPickle** (`.gpickle`): Formato nativo Python para carregamento rápido
- **GraphML** (`.graphml`): Formato XML para interoperabilidade
- **JSON** (`.json`): Formato legível para análise e exportação

**Tipos de Nós:**
- `author`: Autores de artigos
- `institution`: Instituições afiliadas
- `organism`: Organismos estudados (e.g., Homo sapiens, Mus musculus)
- `mesh_term`: Termos MeSH (Medical Subject Headings)
- `journal`: Journals onde artigos foram publicados

**Tipos de Arestas:**
- `authored`: Autor escreveu artigo
- `affiliated_with`: Autor afiliado a instituição
- `studies`: Artigo estuda organismo
- `has_mesh_term`: Artigo possui termo MeSH
- `published_in`: Artigo publicado em journal

## Variáveis de Ambiente

| Variável | Descrição | Padrão | Obrigatório |
|----------|-----------|--------|-------------|
| `GOOGLE_API_KEY` | Chave de API do Google Gemini | - | Sim |
| `GOOGLE_EMBED_MODEL` | Modelo de embedding | `models/text-embedding-004` | Não |
| `GOOGLE_CHAT_MODEL` | Modelo de chat/LLM | `gemini-2.0-flash-exp` | Não |
| `MONGODB_URI` | URI de conexão MongoDB/Cosmos DB | `mongodb://localhost:27017` | Sim |
| `MONGODB_DATABASE` | Nome do banco de dados | `spaceapss` | Não |
| `MONGODB_COLLECTION` | Nome da coleção de artigos | `articles` | Não |
| `REDIS_URL` | URL de conexão Redis | `redis://localhost:6379` | Sim |
| `REDIS_USERNAME` | Usuário Redis (se necessário) | `default` | Não |
| `REDIS_PASSWORD` | Senha Redis | - | Não |
| `API_PORT` | Porta da API FastAPI | `8000` | Não |
| `ENV` | Ambiente de execução | `dev` | Não |
| `CORS_ORIGINS` | Origens permitidas (CORS) | `http://localhost:5173` | Não |
| `GRAPH_PATH` | Caminho do arquivo do Knowledge Graph | `graphs/knowledge_graph_latest.gpickle` | Não |

## Logs

Os logs da aplicação são gerenciados de forma estruturada:

- **Console:** Saída padrão durante desenvolvimento
- **Arquivos:** Logs persistidos em `logs/` em produção

**Níveis de Log:**
- `DEBUG`: Informações detalhadas para debugging (apenas em desenvolvimento)
- `INFO`: Operações normais do sistema
- `WARNING`: Avisos sobre situações inesperadas, mas não críticas
- `ERROR`: Erros que impedem operações específicas
- `CRITICAL`: Falhas graves que podem comprometer o sistema

## Troubleshooting

### Erro: MongoDB Connection Failed

**Sintoma:** `pymongo.errors.ServerSelectionTimeoutError`

**Solução:**
```bash
# Verificar se MongoDB está rodando
sudo systemctl status mongodb  # Linux
# ou
brew services list  # macOS

# Iniciar MongoDB
sudo systemctl start mongodb  # Linux
brew services start mongodb  # macOS

# Ou usar Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Erro: Redis Connection Refused

**Sintoma:** `redis.exceptions.ConnectionError`

**Solução:**
```bash
# Verificar status do Redis
redis-cli ping

# Iniciar Redis localmente
redis-server

# Ou usar Docker
docker run -d -p 6379:6379 --name redis redis:latest
```

### Erro: Google API Key Not Found

**Sintoma:** `ValueError: GOOGLE_API_KEY environment variable not set`

**Solução:**
```bash
# Verificar arquivo .env
cat .env | grep GOOGLE_API_KEY

# Adicionar chave ao .env
echo "GOOGLE_API_KEY=your_key_here" >> .env
```

### Erro: Knowledge Graph Not Found

**Sintoma:** `FileNotFoundError: graphs/knowledge_graph_latest.gpickle not found`

**Solução:**
```bash
# Executar script de construção do grafo
python build_knowledge_graph.py

# Verificar se o arquivo foi criado
ls -lh graphs/
```

### Performance Lenta na Extração de Artigos

**Sintomas:** Pipeline de enriquecimento muito lento

**Otimizações:**
1. Reduzir batch size no `call_and_insert_in_DB.py`
2. Usar modelo LLM mais rápido (ex: `gemini-1.5-flash` em vez de `gemini-1.5-pro`)
3. Verificar limites de rate limit da API do Google
4. Aumentar timeout em requisições à NCBI API

## Recursos Adicionais

- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Framework web usado na API
- [NetworkX Documentation](https://networkx.org/) - Biblioteca de grafos para Knowledge Graph
- [MongoDB Documentation](https://docs.mongodb.com/) - Banco de dados de documentos
- [Azure Cosmos DB](https://docs.microsoft.com/azure/cosmos-db/) - Banco de dados distribuído (compatível com MongoDB)
- [Google Gemini API](https://ai.google.dev/docs) - LLM e modelos de embedding
- [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) - API para extração de artigos científicos
- [vis.js Network](https://visjs.github.io/vis-network/) - Biblioteca de visualização de grafos (frontend)

## Contribuindo

1. Faça fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças seguindo convenções semânticas (`git commit -m 'feat: adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request com descrição detalhada das mudanças

**Convenções de Commit:**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Alterações em documentação
- `refactor:` Refatoração de código
- `test:` Adição ou modificação de testes
- `chore:` Tarefas de manutenção

## Licença

MIT License - Veja o arquivo LICENSE para detalhes.

---

**SpaceAPSS Project** - Space Biology Research with Artificial Intelligence
