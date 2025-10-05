# 🚀 SpaceAPSS - Visão Geral do Projeto

## 📌 Resumo Executivo

**SpaceAPSS** (Space Applied Science Search System) é um sistema de **busca e resposta inteligente** sobre artigos científicos relacionados a pesquisas espaciais, utilizando técnicas de **RAG (Retrieval-Augmented Generation)** e **IA generativa**.

O projeto permite que usuários façam perguntas em linguagem natural e recebam respostas contextualizadas baseadas em uma base de dados de artigos científicos do PubMed/PMC sobre medicina espacial, microbiologia, efeitos da microgravidade, e outros tópicos relacionados.

---

## 🏗️ Arquitetura do Sistema

### Stack Tecnológico

#### **Backend (agents/)**
- **FastAPI** - Framework web assíncrono
- **ChromaDB** - Banco de dados vetorial para embeddings
- **Google Gemini 2.0 Flash** - LLM para geração de respostas
- **Text Embedding 004** - Modelo de embeddings do Google
- **Redis** - Cache e gerenciamento de sessões
- **BeautifulSoup4 + Readability** - Extração de conteúdo web
- **NCBI E-utilities API** - Busca de artigos científicos

#### **Frontend (front/)**
- **React + TypeScript** - Interface do usuário
- **Vite** - Build tool e dev server
- **TailwindCSS** - Estilização
- **Axios** - Cliente HTTP

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                         │
│  - Interface de chat                                         │
│  - Visualização de artigos                                   │
│  - Listagem de fontes                                        │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/REST
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND API (FastAPI)                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Routers (Endpoints)                     │    │
│  │  - /health   - /chat   - /articles                   │    │
│  └──────────────────┬───────────────────────────────────┘    │
│                     ▼                                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Agent Pipeline (RAG)                       │    │
│  │  1. Recebe pergunta                                  │    │
│  │  2. Retrieval (busca semântica)                      │    │
│  │  3. Síntese com LLM                                  │    │
│  │  4. Retorna resposta + fontes                        │    │
│  └──────────────────┬───────────────────────────────────┘    │
│                     │                                         │
│     ┌───────────────┴───────────────┐                        │
│     ▼                               ▼                        │
│  ┌─────────────┐              ┌──────────────┐              │
│  │  Retriever  │              │ Google Gemini │              │
│  └──────┬──────┘              └──────────────┘              │
│         │                                                     │
│         ▼                                                     │
│  ┌─────────────────────┐                                     │
│  │  VectorDBManager    │                                     │
│  │    (ChromaDB)       │                                     │
│  └─────────────────────┘                                     │
└─────────────────────────────────────────────────────────────┘
                 ▲
                 │ Processamento em lote
                 │
┌────────────────┴────────────────────────────────────────────┐
│              EXTRAÇÃO DE DADOS (proccess_batch.py)          │
│  - Lê CSV com links de artigos                              │
│  - Extrai conteúdo via NCBI API                              │
│  - Gera embeddings                                           │
│  - Armazena no ChromaDB                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Pipeline Completa - Fluxo Detalhado

### **FASE 1: Ingestão de Dados (Offline)**

#### 1.1 Processamento em Lote (`proccess_batch.py`)

```
CSV Input
   ↓
[SB_publication_PMC.csv]
   │
   │ Para cada artigo:
   ↓
┌──────────────────────────────────────┐
│ 1. Extração de Conteúdo              │
│    - Identifica PMC ID da URL        │
│    - Busca via NCBI E-utilities API  │
│    - Extrai abstract + conteúdo      │
│    - Fallback: scraping HTML/PDF     │
└─────────────┬────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ 2. Sectionização                     │
│    - Divide em seções lógicas        │
│    - Identifica: Abstract, Intro,    │
│      Methods, Results, Discussion    │
└─────────────┬────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ 3. Armazenamento Vetorial            │
│    - Gera embedding do conteúdo      │
│    - Armazena no ChromaDB            │
│    - Salva metadata: title, URL, ID  │
└─────────────┬────────────────────────┘
              ↓
    [ChromaDB Collection]
    [extracted_data.jsonl]
```

**Detalhes Técnicos:**
- **Extrator**: `extract/extractor.py` + `extract/ncbi_fetcher.py`
- **API NCBI**: Usa `efetch.fcgi` com PMC ID para obter XML estruturado
- **Embeddings**: Gerados automaticamente pelo ChromaDB usando modelo configurável
- **Tempo**: ~30-60 min para 600+ artigos

---

### **FASE 2: Consulta em Tempo Real (Online)**

#### 2.1 Fluxo de uma Pergunta do Usuário

```
┌─────────────────────────────────────────────────────────────┐
│ USUÁRIO                                                      │
│ "Quais são os efeitos da microgravidade em células humanas?"│
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (ChatBox.tsx)                                       │
│ 1. Captura input                                             │
│ 2. Envia POST /chat                                          │
│    Body: { "question": "...", "topK": 5 }                    │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP Request
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ BACKEND - Router (/chat)                                     │
│ - Valida request                                             │
│ - Chama pipeline.answer()                                    │
└─────────────────┬───────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ AGENT PIPELINE (pipeline.py)                                 │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ETAPA 1: RETRIEVAL                                       │ │
│ │                                                           │ │
│ │ retriever.retrieve_with_metadata(question, top_k=5)      │ │
│ │   ↓                                                       │ │
│ │ VectorDBManager.query_with_metadata()                    │ │
│ │   ↓                                                       │ │
│ │ ChromaDB:                                                │ │
│ │   1. Gera embedding da pergunta                          │ │
│ │   2. Busca similaridade cosine                           │ │
│ │   3. Retorna top-k documentos mais similares             │ │
│ │                                                           │ │
│ │ Retorno: Lista de dicts com:                             │ │
│ │   - id: PMC ID do artigo                                 │ │
│ │   - document: Conteúdo completo                          │ │
│ │   - title: Título do artigo                              │ │
│ │   - url: Link original                                   │ │
│ │   - score: Relevância (0-1)                              │ │
│ │   - distance: Distância vetorial                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                   ↓                                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ETAPA 2: VERIFICAÇÃO                                     │ │
│ │                                                           │ │
│ │ if docs_metadata is empty:                               │ │
│ │   return fallback_answer                                 │ │
│ │   (resposta genérica sem contexto)                       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                   ↓                                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ETAPA 3: PREPARAÇÃO DE CONTEXTO                          │ │
│ │                                                           │ │
│ │ Formata documentos para síntese:                         │ │
│ │   "Title: {title}\nContent: {content[:500]}..."          │ │
│ │                                                           │ │
│ │ Constrói prompt estruturado:                             │ │
│ │   - Instrução ao LLM                                     │ │
│ │   - Contexto (documentos recuperados)                    │ │
│ │   - Pergunta do usuário                                  │ │
│ │   - Diretrizes de resposta                               │ │
│ └─────────────────────────────────────────────────────────┘ │
│                   ↓                                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ETAPA 4: SÍNTESE COM LLM                                 │ │
│ │                                                           │ │
│ │ Google Gemini 2.0 Flash:                                 │ │
│ │   - Temperature: 0.3 (respostas mais determinísticas)    │ │
│ │   - Max tokens: 500                                      │ │
│ │   - Modelo: gemini-2.0-flash                             │ │
│ │                                                           │ │
│ │ LLM analisa contexto e gera resposta coerente            │ │
│ └─────────────────────────────────────────────────────────┘ │
│                   ↓                                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ETAPA 5: MONTAGEM DA RESPOSTA                            │ │
│ │                                                           │ │
│ │ Cria objetos estruturados:                               │ │
│ │                                                           │ │
│ │ sources: [SourceRef]                                     │ │
│ │   - Lista de todos os artigos usados                     │ │
│ │   - Com scores de relevância                             │ │
│ │                                                           │ │
│ │ article: Article                                         │ │
│ │   - Artigo mais relevante (top-1)                        │ │
│ │   - Com abstract, URL, metadata                          │ │
│ │                                                           │ │
│ │ answer: string                                           │ │
│ │   - Resposta sintetizada pelo LLM                        │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────┬───────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ RESPOSTA JSON                                                │
│ {                                                             │
│   "answer": "A microgravidade afeta células humanas...",     │
│   "sources": [                                                │
│     {                                                         │
│       "id": "PMC1234567",                                     │
│       "title": "Effects of microgravity...",                  │
│       "score": 0.923,                                         │
│       "url": "https://..."                                    │
│     }                                                         │
│   ],                                                          │
│   "article": {                                                │
│     "id": "PMC1234567",                                       │
│     "title": "...",                                           │
│     "abstract": "...",                                        │
│     "metadata": {...}                                         │
│   }                                                           │
│ }                                                             │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP Response
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND - Renderização                                      │
│                                                               │
│ 1. Exibe resposta do agente                                  │
│ 2. Lista fontes com scores                                   │
│ 3. Link para artigo completo                                 │
│ 4. Modal com detalhes do artigo                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Componentes Detalhados

### 1. **VectorDBManager** (`services/vector_db.py`)

**Responsabilidades:**
- Gerencia conexão com ChromaDB
- Armazena documentos com embeddings
- Executa buscas semânticas (similarity search)
- Retorna metadados estruturados

**Métodos Principais:**
```python
add_document_id(document, metadata, doc_id)
  → Adiciona/atualiza documento com ID específico

query_with_metadata(query_text, n_results)
  → Busca semântica retornando docs estruturados
  → Calcula score: 1.0 - distance (normalizado 0-1)
```

**ChromaDB Collection:**
- Nome: `nasa_space_collection`
- Embedding automático via modelo configurável
- Métrica: Distância cosine

---

### 2. **Retriever** (`agent/retriever.py`)

**Responsabilidades:**
- Interface entre pipeline e VectorDBManager
- Singleton pattern para eficiência
- Logging de operações

**Fluxo:**
```python
retrieve_with_metadata(question, top_k=5)
  ↓
db_manager.query_with_metadata(question, top_k)
  ↓
Retorna: List[Dict] com metadados completos
```

---

### 3. **AgentPipeline** (`agent/pipeline.py`)

**Responsabilidades:**
- Orquestração completa do RAG
- Integração com Google Gemini
- Construção de prompts
- Formatação de respostas

**Prompts:**
```python
build_synthesis_prompt(question, docs)
  → Template estruturado para LLM
  → Inclui contexto e diretrizes
  
build_fallback_prompt(question)
  → Resposta quando não há documentos
  → Explica limitação educadamente
```

---

### 4. **Extração de Dados** (`extract/`)

#### **ncbi_fetcher.py**
- Busca artigos via NCBI E-utilities API
- Parse de XML estruturado
- Extrai: abstract, seções, referências

#### **extractor.py**
- Detecta tipo de conteúdo (HTML/PDF)
- Extração de texto limpo
- Fallback para scraping web

#### **sectionizer.py**
- Identifica seções de artigos científicos
- Padrões: Introduction, Methods, Results, Discussion
- Estrutura hierárquica

---

## 📊 Métricas e Performance

### Busca Semântica (ChromaDB)
- **Latência média**: ~50-100ms para top-5
- **Precisão**: Score > 0.8 indica alta relevância
- **Recall**: Depende da qualidade dos embeddings

### Síntese (Google Gemini)
- **Latência**: ~1-3 segundos
- **Temperature**: 0.3 (baixa variação)
- **Max tokens**: 500 (respostas concisas)

### Processamento Batch
- **Velocidade**: ~5-10 artigos/minuto
- **Taxa de sucesso**: ~80% (alguns artigos sem abstract)
- **Total processado**: 490/607 artigos

---

## 🔐 Segurança e Configuração

### Variáveis de Ambiente (`.env`)
```bash
GOOGLE_API_KEY          # Chave Google Gemini
GOOGLE_EMBED_MODEL      # Modelo de embeddings
GOOGLE_CHAT_MODEL       # Modelo de chat
REDIS_URL              # Conexão Redis
CORS_ORIGINS           # Origens permitidas
ENV                    # dev/prod
```

### CORS
- Configurado para localhost (desenvolvimento)
- Deve ser restrito em produção

### Rate Limiting
- Não implementado (recomendado para produção)
- Redis pode ser usado para isso

---

## 🚀 Fluxo de Desenvolvimento

### Setup Inicial
```bash
# 1. Backend
cd agents
python -m venv .venv
source .venv/bin/activate
pip install -e .
python proccess_batch.py  # ~30-60 min

# 2. Iniciar API
uvicorn packages.api.app.main:app --reload --port 8000

# 3. Frontend
cd ../front
npm install
npm run dev
```

### Adicionar Novos Artigos
```bash
# 1. Atualizar CSV: shared/SB_publication_PMC.csv
# 2. Rodar processamento
python proccess_batch.py
# 3. Reiniciar API (se necessário)
```

---

## 📈 Possíveis Melhorias Futuras

### 1. **Performance**
- [ ] Cache de embeddings de perguntas comuns (Redis)
- [ ] Indexação mais eficiente (HNSW no ChromaDB)
- [ ] Reranking com modelo cross-encoder

### 2. **Funcionalidades**
- [ ] Histórico de conversas persistente
- [ ] Exportar respostas em PDF/Markdown
- [ ] Sugestões de perguntas relacionadas
- [ ] Multi-idioma

### 3. **Qualidade**
- [ ] Fine-tuning do modelo de embeddings
- [ ] Avaliação com métricas (BLEU, ROUGE)
- [ ] A/B testing de prompts
- [ ] Feedback loop do usuário

### 4. **Infraestrutura**
- [ ] Containerização (Docker)
- [ ] CI/CD pipeline
- [ ] Monitoramento (Prometheus/Grafana)
- [ ] Rate limiting e autenticação

---

## 🎯 Casos de Uso

1. **Pesquisadores**: Busca rápida em literatura científica
2. **Estudantes**: Entendimento de conceitos de medicina espacial
3. **Profissionais**: Síntese de múltiplos artigos
4. **Educação**: Ferramenta de aprendizado interativa

---

## 📚 Referências Técnicas

- **RAG Paper**: [Retrieval-Augmented Generation (Lewis et al.)](https://arxiv.org/abs/2005.11401)
- **ChromaDB**: https://docs.trychroma.com/
- **Google Gemini**: https://ai.google.dev/docs
- **FastAPI**: https://fastapi.tiangolo.com/
- **NCBI API**: https://www.ncbi.nlm.nih.gov/books/NBK25501/

---

## 👥 Equipe SpaceAPSS

Desenvolvido como projeto acadêmico/pesquisa em Inteligência Artificial aplicada à literatura científica espacial.

**Licença**: MIT

---

**Última atualização**: Outubro 2025
