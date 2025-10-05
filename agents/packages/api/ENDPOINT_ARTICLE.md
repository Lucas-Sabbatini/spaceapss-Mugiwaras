# Endpoint de Artigos - Documentação

## Endpoint GET /article/{experiment_id}

Busca um artigo enriquecido no MongoDB pelo `experiment_id`.

### URL
```
GET http://localhost:8000/article/{experiment_id}
```

### Parâmetros

- **experiment_id** (path, required): ID do experimento no formato `PMC` + números
  - Exemplo: `PMC9267413`
  - Pode ser passado com ou sem o prefixo `PMC` (o endpoint adiciona automaticamente se necessário)

### Resposta de Sucesso (200)

Retorna um objeto `ArticleDetail` com todos os campos do artigo:

```json
{
  "experiment_id": "PMC9267413",
  "doi": "10.1234/example.doi",
  "title": "Effects of Microgravity on Cell Behavior",
  "abstract": "Original abstract text...",
  "summary_pt": "Summary of the article in English...",
  "year": 2022,
  "authors": ["Author One", "Author Two"],
  "institutions": ["Institution A", "Institution B"],
  "funding": ["Grant 123", "Grant 456"],
  "objectives": ["Objective 1", "Objective 2"],
  "hypotheses": ["Hypothesis 1"],
  "organisms": ["Organism A"],
  "conditions": ["Microgravity", "Radiation"],
  "methods": ["Method 1", "Method 2"],
  "parameters_measured": ["Parameter 1"],
  "results_summary": "Summary of results...",
  "significant_findings": ["Finding 1", "Finding 2"],
  "implications": ["Implication 1"],
  "limitations": ["Limitation 1"],
  "future_directions": ["Direction 1"],
  "duration": "30 days",
  "sample_size": 100,
  "conditions_control": ["Control group 1"],
  "related_projects": ["Project A"],
  "citations": 42,
  "full_text": "Complete article text...",
  "mesh_terms": ["Term 1", "Term 2"],
  "journal": "Nature",
  "pmid": "12345678",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-02T00:00:00"
}
```

### Respostas de Erro

#### 404 - Artigo não encontrado
```json
{
  "detail": "Artigo PMC9267413 não encontrado no banco de dados"
}
```

#### 500 - Erro interno
```json
{
  "detail": "Erro interno ao buscar artigo: [mensagem de erro]"
}
```

## Como Testar

### 1. Via cURL

```bash
# Buscar artigo PMC9267413
curl http://localhost:8000/article/PMC9267413

# Ou sem o prefixo PMC (funciona também)
curl http://localhost:8000/article/9267413

# Com formatação bonita (se tiver jq instalado)
curl http://localhost:8000/article/PMC9267413 | jq
```

### 2. Via Python Script

Execute o script de teste incluído:

```bash
cd agents
python test_article_endpoint.py
```

### 3. Via Swagger UI

Acesse: http://localhost:8000/docs

1. Expanda a seção **articles**
2. Clique em **GET /article/{experiment_id}**
3. Clique em **Try it out**
4. Digite `PMC9267413` no campo `experiment_id`
5. Clique em **Execute**

### 4. Via HTTPie

```bash
# Instalar httpie: pip install httpie
http GET http://localhost:8000/article/PMC9267413
```

## Pré-requisitos

1. **API rodando**:
   ```bash
   cd agents
   uvicorn packages.api.app.main:app --reload
   ```

2. **MongoDB rodando** com dados:
   - Host: `localhost:27017`
   - Database: `spaceapss`
   - Collection: `experiments`

3. **Artigo processado**: O artigo deve ter sido previamente processado pelo pipeline de enriquecimento:
   ```bash
   cd agents
   python example_enrichment.py
   ```

## Configuração

As configurações do MongoDB podem ser ajustadas via variáveis de ambiente no arquivo `.env`:

```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=spaceapss
MONGODB_COLLECTION=experiments
```

## Campos Retornados

### Metadados Básicos
- `experiment_id`: ID único (ex: PMC9267413)
- `title`: Título do artigo
- `authors`: Lista de autores
- `year`: Ano de publicação
- `doi`: Digital Object Identifier
- `pmid`: PubMed ID
- `journal`: Nome do periódico

### Resumos
- `abstract`: Resumo original
- `summary_pt`: Resumo em inglês (gerado por LLM)

### Dados Experimentais (extraídos por NLP)
- `objectives`: Objetivos principais
- `hypotheses`: Hipóteses testadas
- `organisms`: Organismos estudados
- `conditions`: Condições experimentais
- `methods`: Métodos utilizados
- `parameters_measured`: Parâmetros medidos
- `results_summary`: Resumo dos resultados
- `significant_findings`: Descobertas significativas
- `implications`: Implicações práticas/teóricas
- `limitations`: Limitações do estudo
- `future_directions`: Direções futuras
- `duration`: Duração do experimento
- `sample_size`: Tamanho da amostra
- `conditions_control`: Grupos controle
- `related_projects`: Projetos relacionados

### Dados Adicionais
- `institutions`: Instituições dos autores
- `funding`: Fontes de financiamento
- `citations`: Número de citações
- `mesh_terms`: Termos MeSH (Medical Subject Headings)
- `full_text`: Texto completo do artigo
- `created_at`: Data de criação no banco
- `updated_at`: Data de última atualização

## Exemplos de Uso

### Buscar apenas alguns campos

```python
import requests

response = requests.get("http://localhost:8000/article/PMC9267413")
data = response.json()

# Acessar campos específicos
print(f"Título: {data['title']}")
print(f"Resumo PT: {data['summary_pt']}")
print(f"Objetivos: {data['objectives']}")
```

### Listar todos os métodos utilizados

```python
import requests

response = requests.get("http://localhost:8000/article/PMC9267413")
data = response.json()

print("Métodos utilizados:")
for method in data.get('methods', []):
    print(f"  • {method}")
```

### Verificar se artigo existe antes de processar

```python
import requests

def article_exists(experiment_id):
    response = requests.get(f"http://localhost:8000/article/{experiment_id}")
    return response.status_code == 200

if article_exists("PMC9267413"):
    print("Artigo já existe no banco!")
else:
    print("Artigo precisa ser processado")
```

## Integração com Frontend

No frontend React/TypeScript, você pode usar assim:

```typescript
import { api } from './lib/api';

async function fetchArticle(experimentId: string) {
  try {
    const response = await api.get(`/article/${experimentId}`);
    return response.data;
  } catch (error) {
    if (error.response?.status === 404) {
      console.error('Artigo não encontrado');
    }
    throw error;
  }
}
```
