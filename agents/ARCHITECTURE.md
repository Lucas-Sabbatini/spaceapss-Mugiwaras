# 🏗️ Arquitetura do Sistema

## Visão Geral

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENTE (Frontend/cURL)                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          FastAPI Application                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Routers                                                      │   │
│  │  ├─ /health        (Health Check)                           │   │
│  │  ├─ /chat          (POST - Perguntas)                       │   │
│  │  └─ /article/{id}  (GET - Recuperar Artigo)                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                             │                                         │
│                             ▼                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Agent Pipeline                                              │   │
│  │                                                               │   │
│  │  1. Recebe pergunta                                         │   │
│  │  2. Gera embedding da pergunta                              │   │
│  │  3. Busca híbrida (vetorial + textual)                      │   │
│  │  4. Re-rank por score + ano                                 │   │
│  │  5. Sintetiza resposta com LLM                              │   │
│  │  6. Retorna answer + sources + article                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│              │                    │                    │              │
│              ▼                    ▼                    ▼              │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────┐      │
│  │  Retriever   │    │  Embeddings      │    │  LLM Client  │      │
│  │              │    │  Service         │    │  (OpenAI/    │      │
│  │  - KNN       │    │                  │    │   Azure)     │      │
│  │  - BM25      │    │  - OpenAI        │    │              │      │
│  │  - Fallback  │    │  - Azure OpenAI  │    │  - GPT-4o    │      │
│  └──────────────┘    └──────────────────┘    └──────────────┘      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Redis Stack                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  RedisJSON                                                   │   │
│  │  ├─ article:001 → { id, title, authors, abstract, ... }     │   │
│  │  ├─ article:002 → { id, title, authors, abstract, ... }     │   │
│  │  └─ article:003 → { id, title, authors, abstract, ... }     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                             │                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  RediSearch Index (idx:articles)                            │   │
│  │                                                               │   │
│  │  Fields:                                                     │   │
│  │  ├─ $.title       (TEXT - BM25)                             │   │
│  │  ├─ $.abstract    (TEXT - BM25)                             │   │
│  │  ├─ $.year        (NUMERIC - filtro/sort)                   │   │
│  │  ├─ $.doi         (TAG)                                     │   │
│  │  └─ $.embedding   (VECTOR - FLOAT32, dim=1536, COSINE)      │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Fluxo de Dados - Chat Request

```
1. Cliente envia pergunta
   POST /chat {"question": "...", "topK": 5}
          │
          ▼
2. ChatRouter valida request (Pydantic)
          │
          ▼
3. Pipeline.answer(question, top_k)
          │
          ├──▶ EmbeddingsService.get_embedding(question)
          │           │
          │           └──▶ OpenAI API (text-embedding-3-small)
          │                      │
          │                      └──▶ [0.123, 0.456, ..., 0.789] (1536 dims)
          │
          ├──▶ Retriever.retrieve(question, top_k)
          │           │
          │           ├──▶ RedisClient.search_vector(embedding, top_k)
          │           │           │
          │           │           └──▶ Redis: FT.SEARCH idx:articles
          │           │                   "*=>[KNN 5 @embedding $vec]"
          │           │                      │
          │           │                      └──▶ [{id, score}, ...]
          │           │
          │           ├──▶ RedisClient.search_text(question, top_k)
          │           │           │
          │           │           └──▶ Redis: FT.SEARCH idx:articles
          │           │                   "@title|abstract:(question)"
          │           │                      │
          │           │                      └──▶ [{id}, ...]
          │           │
          │           └──▶ Ranker.combine_scores(vector, text, alpha=0.7)
          │                      │
          │                      └──▶ hybrid_score = 0.7*vec + 0.3*text
          │
          ├──▶ Ranker.rerank_by_year(docs)
          │           │
          │           └──▶ adjusted_score = score + year_bonus
          │
          ├──▶ Pipeline._synthesize(question, docs)
          │           │
          │           ├──▶ Prompts.build_synthesis_prompt(question, docs)
          │           │
          │           └──▶ LLM Client (OpenAI/Azure)
          │                   model: gpt-4o-mini
          │                   temperature: 0.3
          │                   max_tokens: 500
          │                      │
          │                      └──▶ "Resposta concisa em PT-BR..."
          │
          └──▶ RedisClient.get_article(top_article_id)
                      │
                      └──▶ Article completo
          
4. Monta ChatResponse
   {
     "answer": "...",
     "sources": [{id, title, year, doi, score}, ...],
     "article": {id, title, authors, abstract, sections, ...}
   }
          │
          ▼
5. Retorna JSON ao cliente
```

## Fluxo de Ingestão

```
1. Samples JSON (data/samples/*.json)
          │
          ▼
2. load_json.py
          │
          ├──▶ Read JSON files
          │
          └──▶ RedisClient.set_article(id, data)
                      │
                      └──▶ Redis: JSON.SET article:{id} $ {...}
          
3. make_embeddings.py
          │
          ├──▶ RedisClient.list_all_keys("article:*")
          │
          ├──▶ Para cada artigo:
          │     │
          │     ├──▶ Utils.build_text_for_embedding(article)
          │     │         │
          │     │         └──▶ title + abstract + sections[0:3]
          │     │
          │     ├──▶ EmbeddingsService.get_embedding(text)
          │     │         │
          │     │         └──▶ OpenAI API → [0.1, 0.2, ..., 0.9]
          │     │
          │     └──▶ RedisClient.update_embedding(id, embedding)
          │                 │
          │                 └──▶ Redis: JSON.SET article:{id} $.embedding [...]
          │
          └──▶ RediSearch automaticamente indexa o novo vetor!
```

## Modo Fallback (sem Redis)

```
Quando Redis não está disponível:

1. Retriever detecta Redis offline
          │
          ▼
2. Carrega samples em memória
   ├─ Lê data/samples/*.json
   └─ Cria estruturas numpy
          │
          ▼
3. Busca local
   ├──▶ Vetorial: cosine_similarity(query_vec, article_vecs)
   │              usando numpy
   │
   └──▶ Textual: TfidfVectorizer.transform(question)
                 scikit-learn TF-IDF
          │
          ▼
4. Combina scores e retorna
   (mesma API, sem diferença para cliente!)
```

## Camadas de Abstração

```
┌──────────────────────────────────────────────────────┐
│  Presentation Layer (FastAPI Routers)                │
│  - Validação de entrada (Pydantic)                   │
│  - Serialização de saída (Pydantic)                  │
│  - Tratamento de erros HTTP                          │
└────────────────┬─────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────┐
│  Business Logic Layer (Agent Pipeline)               │
│  - Orquestração do fluxo                            │
│  - Lógica de retrieval + ranking + synthesis        │
│  - Coordenação entre serviços                       │
└────────────────┬─────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────┐
│  Service Layer                                       │
│  - RedisClient (abstração do DB)                    │
│  - EmbeddingsService (abstração da API)             │
│  - Logger (observabilidade)                         │
└────────────────┬─────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────┐
│  Infrastructure Layer                                │
│  - Redis Stack (database)                           │
│  - OpenAI API (embeddings + LLM)                    │
│  - Docker (containerização)                         │
└──────────────────────────────────────────────────────┘
```

## Tecnologias por Componente

| Componente | Tecnologias |
|------------|------------|
| **API** | FastAPI, Uvicorn, Pydantic v2 |
| **Agent** | Python 3.11+, vanilla (sem LangChain) |
| **Database** | Redis Stack (RedisJSON + RediSearch) |
| **Embeddings** | OpenAI text-embedding-3-small (1536 dims) |
| **LLM** | OpenAI gpt-4o-mini |
| **Fallback** | numpy, scikit-learn (TF-IDF) |
| **Tests** | pytest, pytest-asyncio |
| **Lint/Format** | ruff, black |
| **Container** | Docker Compose |

## Decisões de Arquitetura

### 1. Por que Redis Stack?
- ✅ RedisJSON: armazenamento nativo de JSON
- ✅ RediSearch: busca vetorial + textual no mesmo índice
- ✅ Performance: latência sub-milissegundo
- ✅ Escalabilidade: fácil escalar horizontalmente

### 2. Por que Busca Híbrida?
- ✅ Vetorial (KNN): captura similaridade semântica
- ✅ Textual (BM25): captura matches exatos de termos
- ✅ Combinação (0.7 + 0.3): melhor de ambos mundos

### 3. Por que Re-rank por Ano?
- ✅ Artigos recentes geralmente mais relevantes
- ✅ Bônus pequeno (10%) não domina o score semântico
- ✅ Facilmente ajustável via parâmetro

### 4. Por que Vanilla (sem LangChain)?
- ✅ Código mais limpo e direto
- ✅ Menos dependências
- ✅ Mais controle sobre o fluxo
- ✅ Fácil migrar para LC depois se necessário

### 5. Por que Modo Fallback?
- ✅ Desenvolvimento sem Docker
- ✅ Testes sem infraestrutura
- ✅ Resiliência em produção
- ✅ Demonstração offline

## Segurança

- 🔒 API Keys via variáveis de ambiente
- 🔒 Validação de entrada (Pydantic)
- 🔒 Sanitização de queries (escape)
- 🔒 CORS configurável
- 🔒 Rate limiting (TODO)
- 🔒 Autenticação (TODO)

## Observabilidade

- 📊 Logs estruturados (logger.py)
- 📊 Health check endpoint
- 📊 Métricas de performance (TODO: Prometheus)
- 📊 Tracing distribuído (TODO: OpenTelemetry)

## Escalabilidade

Componente | Estratégia
-----------|------------
**API** | Múltiplas instâncias + Load Balancer
**Redis** | Redis Cluster + Read Replicas
**Embeddings** | Cache + Batch processing
**LLM** | Queue + Workers paralelos
