# Alterações nas Interfaces TypeScript - Sources e Article

## 📋 Resumo

Implementamos a lógica completa para retornar `sources` e `article` no endpoint da API, com base nos dados disponíveis no ChromaDB.

## ✅ Implementações Realizadas

### 1. **Novo Método no VectorDBManager**

```python
def query_with_metadata(self, query_text: str, n_results: int = 2) -> list[dict]:
    """
    Retorna dados estruturados dos documentos:
    - id: ID do documento
    - document: Conteúdo indexado (abstract)
    - title: Título extraído dos metadados
    - url: URL extraída dos metadados
    - content: Conteúdo completo extraído dos metadados
    - distance: Distância vetorial
    - score: Score de similaridade (1 - distance)
    """
```

### 2. **Novo Método no Retriever**

```python
def retrieve_with_metadata(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Usa query_with_metadata para retornar dados estruturados
    """
```

### 3. **Pipeline Atualizado**

O pipeline agora:
- ✅ Usa `retrieve_with_metadata()` para obter dados estruturados
- ✅ Monta array `sources` a partir dos resultados
- ✅ Monta objeto `article` a partir do resultado mais relevante
- ✅ Retorna `ChatResponse` completo

### 4. **Schemas Atualizados**

Ajustamos os schemas para refletir os dados disponíveis.

## ⚠️ Alterações Necessárias nas Interfaces TypeScript

### Interface `Article` - Campos Alterados

```typescript
export interface Article {
  id: string;  // ✅ OK - Disponível (PMC ID)
  title: string;  // ✅ OK - Disponível
  authors: string[];  // ⚠️ SEMPRE VAZIO [] - Dados não disponíveis
  year: number;  // ⚠️ AGORA OPCIONAL: number | null
  doi?: string;  // ⚠️ SEMPRE null - Dados não disponíveis
  url?: string;  // ✅ OK - Disponível
  abstract: string;  // ⚠️ MUDANÇA: Agora usa o 'document' (conteúdo indexado)
  sections?: Section[];  // ⚠️ SEMPRE null - Dados não disponíveis
  references?: string[];  // ⚠️ SEMPRE null - Dados não disponíveis
  metadata?: Record<string, any>;  // ✅ OK - Contém score, source, full_content
}
```

**Nova Interface Recomendada:**

```typescript
export interface Article {
  id: string;
  title: string;
  authors: string[];  // Sempre vazio
  year: number | null;  // Mudado para opcional/null
  doi?: string | null;
  url?: string;
  abstract: string;  // Conteúdo do documento indexado
  sections?: Section[] | null;  // Mudado para aceitar null
  references?: string[] | null;  // Mudado para aceitar null
  metadata?: {
    score?: number;
    source?: string;
    full_content?: string;
    [key: string]: any;
  };
}
```

### Interface `SourceRef` - Sem Mudanças Críticas

```typescript
export interface SourceRef {
  id: string;  // ✅ OK
  title: string;  // ✅ OK
  year?: number | null;  // ⚠️ SEMPRE null
  doi?: string | null;  // ⚠️ SEMPRE null
  url?: string;  // ✅ OK
  score?: number;  // ✅ OK - Valor entre 0.0 e 1.0 (normalizado)
}
```

**Interface Atualizada:**

```typescript
export interface SourceRef {
  id: string;
  title: string;
  year: number | null;  // Explicitamente null
  doi: string | null;  // Explicitamente null
  url?: string;
  score?: number;  // Sempre >= 0 e <= 1, normalizado com max(0, min(1, 1 - distance))
}
```

### Interface `ChatResponse` - Sem Mudanças

```typescript
export interface ChatResponse {
  answer: string;  // ✅ OK
  sources: SourceRef[];  // ✅ OK - Agora populado
  article: Article | null;  // ✅ OK - Agora populado ou null
}
```

## 📊 Exemplo de Resposta Real

```json
{
  "answer": "Fungos expostos à microgravidade na ISS incluem Aspergillus niger...",
  "sources": [
    {
      "id": "PMC5391430",
      "title": "Draft Genome Sequences of Several Fungal Strains Selected for Exposure to Microgravity",
      "year": null,
      "doi": null,
      "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5391430/",
      "score": 0.847
    },
    {
      "id": "PMC7317102",
      "title": "Draft Genome Sequences of Tremellomycetes Strains Isolated from ISS",
      "year": null,
      "doi": null,
      "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7317102/",
      "score": 0.823
    }
  ],
  "article": {
    "id": "PMC5391430",
    "title": "Draft Genome Sequences of Several Fungal Strains Selected for Exposure to Microgravity",
    "authors": [],
    "year": null,
    "doi": null,
    "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5391430/",
    "abstract": "In a screening project of natural products, fungal strains isolated...",
    "sections": null,
    "references": null,
    "metadata": {
      "score": 0.847,
      "source": "ChromaDB",
      "full_content": "GENOME ANNOUNCEMENT In a screening project..."
    }
  }
}
```

## 🔧 Alterações no Frontend Necessárias

### 1. **Tratamento de Campos Null**

```typescript
// Antes
const year = article.year;  // Assumia sempre presente
const authors = article.authors.join(', ');  // Assumia array não vazio

// Depois
const year = article.year ?? 'Ano não disponível';
const authors = article.authors.length > 0 
  ? article.authors.join(', ') 
  : 'Autores não disponíveis';
```

### 2. **Exibição do Article**

```typescript
function ArticleCard({ article }: { article: Article }) {
  return (
    <div>
      <h3>{article.title}</h3>
      <p><strong>ID:</strong> {article.id}</p>
      
      {article.url && (
        <a href={article.url} target="_blank">Ver artigo original</a>
      )}
      
      <p><strong>Abstract:</strong> {article.abstract}</p>
      
      {/* Metadados adicionais */}
      {article.metadata?.score && (
        <p><strong>Relevância:</strong> {(article.metadata.score * 100).toFixed(1)}%</p>
      )}
      
      {/* Campos que sempre estarão vazios/null */}
      {/* NÃO renderizar authors, year, doi, sections, references */}
    </div>
  );
}
```

### 3. **Exibição das Sources**

```typescript
function SourcesList({ sources }: { sources: SourceRef[] }) {
  return (
    <div>
      <h4>Fontes ({sources.length})</h4>
      {sources.map((source, idx) => (
        <div key={source.id}>
          <span>{idx + 1}. {source.title}</span>
          {source.score && (
            <span> ({(source.score * 100).toFixed(1)}% relevante)</span>
          )}
          {source.url && (
            <a href={source.url} target="_blank"> [Ver]</a>
          )}
        </div>
      ))}
    </div>
  );
}
```

## 📝 Resumo das Mudanças por Campo

| Campo | Status Anterior | Status Atual | Observações |
|-------|----------------|--------------|-------------|
| `id` | ✅ Obrigatório | ✅ Obrigatório | PMC ID disponível |
| `title` | ✅ Obrigatório | ✅ Obrigatório | Sempre disponível |
| `authors` | ✅ Obrigatório array | ⚠️ Array vazio `[]` | Não disponível nos dados |
| `year` | ✅ Obrigatório number | ⚠️ `null` | Não disponível nos dados |
| `doi` | ✅ Opcional | ⚠️ Sempre `null` | Não disponível nos dados |
| `url` | ✅ Opcional | ✅ Opcional | Disponível quando houver |
| `abstract` | ✅ Obrigatório | ⚠️ Mudança de uso | Agora usa `document` do ChromaDB |
| `sections` | ✅ Opcional | ⚠️ Sempre `null` | Não disponível nos dados |
| `references` | ✅ Opcional | ⚠️ Sempre `null` | Não disponível nos dados |
| `metadata` | ✅ Opcional | ✅ Opcional | Agora contém score e full_content |

## 🎯 Recomendações

### Para o Backend (Python/API)

1. ✅ **Implementado**: Método `query_with_metadata()`
2. ✅ **Implementado**: Parse de metadata string
3. ✅ **Implementado**: Montagem de `sources` e `article`
4. ⚠️ **Futuro**: Extrair year, doi, authors do conteúdo com regex/LLM

### Para o Frontend (TypeScript/React)

1. ⚠️ **Atualizar interfaces** conforme documentado acima
2. ⚠️ **Adicionar null checks** em todos os campos opcionais
3. ⚠️ **Esconder campos vazios** (authors, year, doi, sections, references)
4. ✅ **Usar metadata.score** para mostrar relevância
5. ✅ **Usar metadata.full_content** para preview expandido

## 🚀 Próximos Passos

### Melhorias Sugeridas

1. **Extrair Metadados do Conteúdo**
   - Usar regex para extrair year do texto
   - Usar LLM para extrair authors
   - Buscar DOI no texto

2. **Enriquecer Dados no Proccess Batch**
   ```python
   # Ao adicionar documento, já extrair metadados
   metadata = {
       'title': extract_title(content),
       'year': extract_year(content),
       'authors': extract_authors(content),
       'url': url
   }
   ```

3. **Cache de Artigos Completos**
   - Salvar artigos completos em arquivo JSON
   - Buscar de lá quando precisar de dados completos

## ✅ Conclusão

A API agora retorna `sources` e `article` corretamente, mas com limitações nos dados devido à estrutura atual do ChromaDB. As interfaces TypeScript precisam ser atualizadas para aceitar `null` em campos que não estão disponíveis nos dados atuais.
