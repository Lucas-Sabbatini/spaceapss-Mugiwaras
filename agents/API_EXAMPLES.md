# 📖 Exemplos de Uso da API

## Base URL
```
http://localhost:8000
```

## 1. Health Check

### Request
```bash
curl http://localhost:8000/health
```

### Response
```json
{
  "status": "ok",
  "redis": "connected",
  "version": "0.1.0"
}
```

## 2. Chat - Fazer Pergunta

### Request
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quais efeitos da microgravidade em células-tronco?",
    "topK": 5
  }'
```

### Response
```json
{
  "answer": "Estudos mostram que a microgravidade afeta significativamente a diferenciação de células-tronco mesenquimais (MSCs). Silva et al. (2023) observaram um aumento de 2.5 vezes no potencial osteogênico e redução de 60% na diferenciação adipogênica após 14 dias de exposição simulada. A expressão de fatores de transcrição chave como RUNX2 e OSX aumentou 3.2 e 2.8 vezes, respectivamente. Essas alterações são mediadas por vias de mecanotransdução, representando uma resposta celular adaptativa ao ambiente de microgravidade (Effects of Microgravity on Stem Cell Differentiation and Proliferation, 2023, 10.1038/s41526-023-00001-x).",
  "sources": [
    {
      "id": "art-001",
      "title": "Effects of Microgravity on Stem Cell Differentiation and Proliferation",
      "year": 2023,
      "doi": "10.1038/s41526-023-00001-x",
      "url": "https://www.nature.com/articles/s41526-023-00001-x",
      "score": 0.89
    }
  ],
  "article": {
    "id": "art-001",
    "title": "Effects of Microgravity on Stem Cell Differentiation and Proliferation",
    "authors": ["Silva, J.P.", "Santos, M.A.", "Costa, R.F.", "Oliveira, L.M."],
    "year": 2023,
    "doi": "10.1038/s41526-023-00001-x",
    "url": "https://www.nature.com/articles/s41526-023-00001-x",
    "abstract": "Microgravity environments present unique challenges...",
    "sections": [...],
    "references": [...],
    "metadata": {...}
  }
}
```

## 3. Mais Exemplos de Perguntas

### Radiação Espacial
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Como proteger astronautas da radiação em missões para Marte?"
  }'
```

### Saúde Cardiovascular
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quais adaptações cardiovasculares ocorrem durante voos espaciais longos?"
  }'
```

### Comparação de Estudos
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qual a relação entre microgravidade e sistemas biológicos?",
    "topK": 10
  }'
```

## 4. Recuperar Artigo por ID

### Request
```bash
curl http://localhost:8000/article/art-001
```

### Response
```json
{
  "id": "art-001",
  "title": "Effects of Microgravity on Stem Cell Differentiation and Proliferation",
  "authors": ["Silva, J.P.", "Santos, M.A.", "Costa, R.F.", "Oliveira, L.M."],
  "year": 2023,
  "doi": "10.1038/s41526-023-00001-x",
  "url": "https://www.nature.com/articles/s41526-023-00001-x",
  "abstract": "Microgravity environments present unique challenges...",
  "sections": [
    {
      "heading": "Introduction",
      "content": "Space exploration and long-duration missions..."
    },
    {
      "heading": "Methods",
      "content": "Human mesenchymal stem cells were cultured..."
    }
  ],
  "references": [
    "Chen, Z. et al. (2022) Mechanotransduction in stem cells...",
    "Grimm, D. et al. (2021) The impact of microgravity..."
  ],
  "metadata": {
    "keywords": ["microgravity", "stem cells", "differentiation"],
    "journal": "npj Microgravity",
    "impact_factor": 4.8
  }
}
```

## 5. Root Endpoint

### Request
```bash
curl http://localhost:8000/
```

### Response
```json
{
  "message": "SpaceAPSS Agents API",
  "version": "0.1.0",
  "docs": "/docs",
  "health": "/health"
}
```

## 6. Documentação Interativa

Acesse no navegador:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 7. PowerShell (Windows)

Para Windows PowerShell, use aspas duplas e escape:

```powershell
curl.exe -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d "{`"question`":`"Quais efeitos da microgravidade?`",`"topK`":5}"
```

Ou use `Invoke-WebRequest`:

```powershell
$body = @{
    question = "Quais efeitos da microgravidade em células-tronco?"
    topK = 5
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/chat `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

## 8. Python Requests

```python
import requests

# Chat
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "question": "Quais efeitos da microgravidade em células-tronco?",
        "topK": 5
    }
)
data = response.json()
print(data["answer"])

# Get article
article = requests.get("http://localhost:8000/article/art-001").json()
print(article["title"])
```

## 9. JavaScript/Fetch

```javascript
// Chat
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'Quais efeitos da microgravidade em células-tronco?',
    topK: 5
  })
});
const data = await response.json();
console.log(data.answer);

// Get article
const article = await fetch('http://localhost:8000/article/art-001')
  .then(r => r.json());
console.log(article.title);
```

## 10. Tratamento de Erros

### Artigo não encontrado (404)
```bash
curl http://localhost:8000/article/art-999
```
```json
{
  "detail": "Artigo 'art-999' não encontrado"
}
```

### Pergunta muito curta (422)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Hi"}'
```
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "question"],
      "msg": "String should have at least 3 characters"
    }
  ]
}
```

### Erro interno do servidor (500)
```json
{
  "detail": "Erro ao processar pergunta: [mensagem de erro]"
}
```

## 11. Perguntas em Português

A API responde em português brasileiro automaticamente:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Como a radiação cósmica afeta os astronautas?"
  }'
```

Resposta será em PT-BR com citações dos artigos.
