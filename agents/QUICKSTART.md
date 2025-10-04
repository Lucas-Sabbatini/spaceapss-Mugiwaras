# Quick Start Guide

## 1. Instalar Dependências

```bash
# Instalar pacote em modo editable
pip install -e ".[dev]"
```

## 2. Configurar Ambiente

```bash
# Copiar .env.example para .env
cp .env.example .env

# Editar .env e adicionar sua OPENAI_API_KEY
nano .env  # ou vim .env
```

**Variáveis necessárias no `.env`:**
```
PROVIDER=openai
OPENAI_API_KEY=sua-chave-aqui
OPENAI_CHAT_MODEL=gpt-3.5-turbo
```

## 3. Preparar ChromaDB

O sistema usa ChromaDB como banco de dados vetorial. Certifique-se de que o diretório `chroma_db` existe:

```bash
# O diretório chroma_db deve estar no nível superior do projeto
ls -la ../../chroma_db
```

## 4. Popular o ChromaDB

**Opção 1: Usar script automático (Recomendado)**

```bash
# Popular com 10 documentos de exemplo sobre ciências espaciais
python populate_chromadb.py
```

Este script adiciona documentos sobre:
- Efeitos da microgravidade em células-tronco
- Aplicações biomédicas de pesquisas espaciais
- Efeitos da radiação em células humanas
- Atrofia muscular e perda de densidade óssea
- E muito mais...

**Opção 2: Adicionar documentos manualmente**

```python
from packages.api.app.services.vector_db import VectorDBManager

db = VectorDBManager()

# Adicionar seus próprios documentos
db.add_document(
    document="Seu texto completo do artigo aqui...",
    text="https://fonte-do-artigo.com"
)
```

## 5. Iniciar API

```bash
uvicorn packages.api.app.main:app --reload --port 8000
```

Acesse http://localhost:8000/docs para ver a documentação interativa.

## 6. Testar

```bash
# Health check
curl http://localhost:8000/health

# Fazer uma pergunta
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Quais efeitos da microgravidade em células-tronco?","topK":5}'
```

**Resposta esperada:**
```json
{
  "answer": "Baseado nos documentos encontrados...",
  "sources": [],
  "article": null
}
```

## 7. Testar Integração

Execute o script de teste de integração:

```bash
python test_integration.py
```

## Comandos Úteis

```bash
# Rodar testes
pytest

# Formatar código
black packages/

# Lint
ruff check packages/

# Ver logs em tempo real
tail -f logs/app.log
```

## Estrutura Simplificada

O sistema agora funciona com um fluxo simplificado **sem Redis**:

```
Pergunta → VectorDBManager.query() → Lista de Strings → LLM → Resposta
```

**Componentes:**
- ✅ **ChromaDB**: Armazena documentos e faz busca vetorial
- ✅ **VectorDBManager**: Interface simples para ChromaDB
- ✅ **Retriever**: Wrapper que usa VectorDBManager
- ✅ **Pipeline**: Orquestra retrieval + LLM
- ✅ **OpenAI/Azure**: Gera respostas baseadas no contexto

**Removidos (não são mais necessários):**
- ❌ Redis / Redis Stack
- ❌ Docker Compose
- ❌ Embeddings service separado
- ❌ TF-IDF
- ❌ Busca híbrida complexa
- ❌ Re-ranking

## Troubleshooting

### ChromaDB não encontrado
```bash
# Verifique se o diretório existe
ls -la ../../chroma_db

# Se não existir, será criado automaticamente na primeira execução
```

### Erro "Import chromadb could not be resolved"
```bash
# Instalar ChromaDB
pip install chromadb
```

### Erro ao gerar resposta (LLM)
- Verifique se `OPENAI_API_KEY` está configurado no `.env`
- Teste a chave em https://platform.openai.com/api-keys
- Verifique se tem créditos disponíveis

### API não inicia
```bash
# Verifique se porta 8000 está livre
lsof -i :8000

# Tente outra porta
uvicorn packages.api.app.main:app --port 8001
```

### Nenhum documento encontrado
- Verifique se o ChromaDB foi populado
- Use o script de teste para adicionar documentos de exemplo
- Confira o caminho do ChromaDB no `VectorDBManager.__init__`

### Respostas genéricas/ruins
- **Problema**: O `VectorDBManager.query()` retorna apenas metadados (`"source"`)
- **Solução**: Modifique o método para retornar documentos completos:

```python
# Em packages/api/app/services/vector_db.py
def query(self, query_text: str, n_results: int = 2) -> list[str]:
    results = self.collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    # Retornar documentos ao invés de metadados
    documents = results.get("documents", [[]])[0]
    return documents
```

## Próximos Passos

1. **Adicionar mais documentos** ao ChromaDB
2. **Ajustar prompts** em `packages/api/app/agent/prompts.py`
3. **Configurar LLM** (modelo, temperatura, max_tokens)
4. **Testar com diferentes perguntas**

## Documentação Adicional

- 📖 **CHANGES.md** - Detalhes das alterações realizadas
- 📖 **ARCHITECTURE.md** - Arquitetura do sistema
- 📖 **API_EXAMPLES.md** - Exemplos de uso da API
- 📖 **TROUBLESHOOTING.md** - Soluções para problemas comuns
