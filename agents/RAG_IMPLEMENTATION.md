# Implementação RAG (Retrieval-Augmented Generation)

## 📋 Visão Geral

Sistema RAG completo para busca semântica e geração de respostas sobre artigos científicos usando MongoDB Atlas Vector Search e Google Generative AI.

## 🏗️ Arquitetura

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Chat Endpoint (chat.py)         │
│  POST /chat                             │
│  - Recebe pergunta do usuário           │
│  - Retorna resposta + sources + article │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│      AgentPipeline (pipeline.py)        │
│  1. Retrieval (via Retriever)           │
│  2. Context Building (campos essenciais)│
│  3. LLM Synthesis (Google Gemini)       │
│  4. Response Formatting                 │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│       Retriever (retriever.py)          │
│  - Usa MongoDataManager                 │
│  - Retorna List[ArticleMetadata]        │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   MongoDataManager (mongo_data.py)      │
│  - query(): Vector Search               │
│  - _get_embedding(): Google GenAI       │
│  - Retorna ArticleMetadata objects      │
└─────────────────────────────────────────┘
```

## 🎯 Campos Essenciais para RAG (Nível 1)

Os campos mais importantes para **Recuperação** e **Geração** são priorizados no contexto enviado ao LLM:

### 1. **experiment_id** (Identificação única)
- Usado para tracking e referências

### 2. **title** (Resumo de alto nível)
- Captura a intenção principal do estudo
- Primeira linha do contexto

### 3. **abstract** (Campo mais importante)
- Resumo denso de todo o trabalho
- Contém objetivos, métodos, resultados e conclusões
- Alta densidade semântica

### 4. **results_summary** (Descobertas principais)
- Vital para responder "O que o estudo descobriu?"
- Foco em resultados concretos

### 5. **significant_findings** (Subconjunto focado)
- Descobertas específicas de alto impacto
- Ideal para buscas por descobertas específicas

### 6. **objectives** e **hypotheses** (Propósito do estudo)
- Essenciais para entender "Por que este estudo foi feito?"
- Contexto de motivação

### 7. **methods** (Metodologia)
- Fundamental para perguntas sobre "Como eles fizeram isso?"
- Credibilidade científica

### 8. **implications** e **future_directions** (Impacto)
- Chave para perguntas analíticas
- Próximos passos e impacto da pesquisa

## 📊 Fluxo de Dados

### 1. Entrada do Usuário
```json
{
  "question": "What are the effects of microgravity on cell behavior?",
  "topK": 5
}
```

### 2. Retrieval (Vector Search)
```python
articles: List[ArticleMetadata] = retriever.retrieve(question, top_k=5)
```

**MongoDB Query:**
```javascript
db.articles.aggregate([
  {
    $vectorSearch: {
      index: "vector_index",
      queryVector: [0.123, 0.456, ...], // 768 dimensões
      path: "embedding",
      exact: true,
      limit: 5
    }
  }
])
```

### 3. Context Building
```python
# Para cada artigo, extrair campos essenciais
context = f"""
TITLE: {article.title}
ABSTRACT: {article.abstract}
OBJECTIVES: {'; '.join(article.objectives)}
HYPOTHESES: {'; '.join(article.hypotheses)}
METHODS: {'; '.join(article.methods)}
RESULTS: {article.results_summary}
KEY FINDINGS: {'; '.join(article.significant_findings)}
IMPLICATIONS: {'; '.join(article.implications)}
FUTURE DIRECTIONS: {'; '.join(article.future_directions)}
"""
```

### 4. LLM Synthesis
```python
# Google Gemini recebe:
# - Pergunta do usuário
# - Contexto dos top-k artigos
# - Instruções para sintetizar resposta

response = model.generate_content(
    prompt=build_synthesis_prompt(question, docs),
    temperature=0.3,
    max_output_tokens=500
)
```

### 5. Response Assembly
```json
{
  "answer": "Based on the retrieved studies, microgravity affects...",
  "sources": [
    {
      "id": "PMC9267413",
      "title": "Effects of Microgravity on Cell Behavior",
      "year": 2022,
      "doi": "10.1234/example",
      "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9267413/"
    }
  ],
  "article": {
    "id": "PMC9267413",
    "title": "Effects of Microgravity on Cell Behavior",
    "authors": ["John Doe", "Jane Smith"],
    "abstract": "This study investigates...",
    "metadata": {
      "organisms": ["Human cells", "E. coli"],
      "conditions": ["Microgravity", "Simulated space environment"],
      "sample_size": 100
    }
  }
}
```

## 🔧 Componentes Atualizados

### 1. **retriever.py**
- **Antes:** Retornava `List[str]` ou dicts genéricos
- **Agora:** Retorna `List[ArticleMetadata]` tipado
- **Benefício:** Type safety, estrutura rica

### 2. **pipeline.py**
- **Antes:** Contexto simples com `title + content[:500]`
- **Agora:** Contexto rico com 9 campos essenciais estruturados
- **Benefício:** LLM recebe informação muito mais relevante

### 3. **mongo_data.py**
- **Implementado:** Função `query()` com vector search
- **Retorna:** `List[ArticleMetadata]` diretamente do MongoDB
- **Benefício:** Integração nativa com embeddings

### 4. **schemas.py**
- **Removido:** Campo `full_text` (não mais usado)
- **Mantido:** Todos os campos essenciais para RAG
- **Benefício:** Schema mais limpo e focado

## ⚙️ Configuração

### 1. Environment Variables
```bash
# .env
GOOGLE_API_KEY=your_google_api_key_here
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DATABASE=spaceapss
MONGODB_COLLECTION=articles
GOOGLE_EMBED_MODEL=models/text-embedding-004
```

### 2. MongoDB Atlas Setup
```python
# Criar índice vetorial (apenas uma vez)
manager = MongoDataManager()
manager.create_vector_index(num_dimensions=768)
```

### 3. Inserir Artigos
```python
# Via enrichment pipeline
pipeline = EnrichmentPipeline(
    google_api_key=GOOGLE_API_KEY,
    mongodb_uri=MONGODB_URI
)
await pipeline.process_batch(pmc_list)
```

## 📈 Performance

### Embedding Generation
- **Modelo:** `text-embedding-004` (Google)
- **Dimensões:** 768
- **Task Type:** `retrieval_document`
- **Tempo:** ~200ms por embedding

### Vector Search
- **Engine:** MongoDB Atlas Vector Search
- **Similarity:** Cosine similarity
- **Latência:** ~100-300ms (depende do tamanho da collection)
- **Precision:** Alta (exact=True)

### LLM Synthesis
- **Modelo:** Google Gemini (gemini-2.0-flash)
- **Temperature:** 0.3 (respostas consistentes)
- **Max Tokens:** 500
- **Tempo:** ~1-3s

## 🎯 Vantagens do Novo Sistema

### 1. **Contexto Rico e Estruturado**
- Não envia texto "cru" para o LLM
- Campos organizados e rotulados
- Foco em informação de alta densidade semântica

### 2. **Type Safety**
- `ArticleMetadata` é um dataclass tipado
- Menos erros em runtime
- IntelliSense/autocomplete funcionam

### 3. **Separação de Preocupações**
- **Retrieval:** MongoDataManager (vector search)
- **Processing:** AgentPipeline (context building)
- **Generation:** Google Gemini (synthesis)

### 4. **Escalabilidade**
- MongoDB Atlas escala automaticamente
- Embeddings pré-computados (não recalculados na query)
- Cache do LLM pode ser adicionado

### 5. **Rastreabilidade**
- Cada artigo tem `experiment_id` único
- Sources retornam PMC URLs
- Metadata completa disponível

## 🚀 Próximos Passos

### 1. **Hybrid Search**
- Combinar vector search com keyword search (BM25)
- Melhor cobertura para queries específicas

### 2. **Reranking**
- Adicionar camada de reranking após retrieval
- Modelos específicos (cross-encoders)

### 3. **Chunking Estratégico**
- Dividir artigos longos em chunks menores
- Overlap entre chunks para contexto

### 4. **Caching**
- Cache de embeddings de queries comuns
- Cache de respostas do LLM

### 5. **Feedback Loop**
- Coletar feedback do usuário sobre relevância
- Fine-tuning do modelo de embeddings

## 📝 Exemplo de Uso

### Request
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What organisms were studied in microgravity experiments?",
    "topK": 3
  }'
```

### Response
```json
{
  "answer": "Based on the retrieved studies, several organisms have been studied in microgravity experiments including: Human cells (particularly stem cells and immune cells), E. coli bacteria, C. elegans nematodes, and Arabidopsis plants. These studies revealed that microgravity affects cell proliferation, gene expression, and metabolic pathways across different species.",
  "sources": [
    {
      "id": "PMC9267413",
      "title": "Effects of Microgravity on Human Stem Cells",
      "year": 2022,
      "doi": "10.1234/example1",
      "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9267413/"
    },
    {
      "id": "PMC8765432",
      "title": "Bacterial Adaptation in Space Environment",
      "year": 2021,
      "doi": "10.1234/example2",
      "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8765432/"
    }
  ],
  "article": {
    "id": "PMC9267413",
    "title": "Effects of Microgravity on Human Stem Cells",
    "authors": ["Dr. Jane Smith", "Dr. John Doe"],
    "year": 2022,
    "abstract": "This study investigates the effects of microgravity...",
    "metadata": {
      "organisms": ["Human stem cells", "MSC cells"],
      "conditions": ["Microgravity", "ISS conditions"],
      "duration": "14 days",
      "sample_size": 50
    }
  }
}
```

## 🎓 Referências

- [MongoDB Atlas Vector Search](https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-overview/)
- [Google Generative AI Embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- [RAG Best Practices](https://www.promptingguide.ai/techniques/rag)
