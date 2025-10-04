# 🔧 Troubleshooting Guide

Soluções para problemas comuns ao usar o sistema.

## 🚨 Problemas de Instalação

### Erro: "pip: command not found"
**Causa:** Python/pip não está instalado ou não está no PATH.

**Solução:**
```powershell
# Instalar Python 3.11+ de python.org
# Ou usar Chocolatey:
choco install python311

# Verificar instalação
python --version
pip --version
```

### Erro: "No module named 'packages'"
**Causa:** Pacote não foi instalado em modo editable.

**Solução:**
```powershell
# Instalar em modo editable
pip install -e ".[dev]"

# Verificar instalação
pip list | findstr spaceapss
```

### Erro ao instalar dependências (conflitos)
**Solução:**
```powershell
# Criar ambiente virtual limpo
python -m venv venv
.\venv\Scripts\activate

# Instalar
pip install --upgrade pip
pip install -e ".[dev]"
```

## 🐳 Problemas com Docker

### Docker Desktop não inicia
**Solução Windows:**
```powershell
# 1. Verificar se WSL2 está instalado
wsl --list --verbose

# 2. Se não, instalar WSL2
wsl --install

# 3. Reiniciar Docker Desktop
```

### "Cannot connect to Docker daemon"
**Solução:**
```powershell
# Iniciar Docker Desktop manualmente
# Ou via linha de comando:
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Verificar se está rodando
docker ps
```

### "Port 6379 is already allocated"
**Causa:** Redis já está rodando ou porta em uso.

**Solução:**
```powershell
# Opção 1: Parar Redis existente
docker compose down

# Opção 2: Verificar processos na porta
netstat -ano | findstr 6379

# Opção 3: Mudar porta no docker-compose.yml
ports:
  - "6380:6379"  # Use 6380 em vez de 6379
```

### Redis não conecta após "docker compose up"
**Solução:**
```powershell
# Aguardar Redis inicializar (pode levar 5-10s)
timeout /t 10

# Verificar logs
docker compose logs redis

# Verificar se está rodando
docker ps

# Testar conexão
docker exec spaceapss-redis redis-cli ping
# Esperado: PONG
```

## 🔑 Problemas com OpenAI API

### "AuthenticationError: Invalid API key"
**Solução:**
```powershell
# 1. Verificar se .env existe
dir .env

# 2. Verificar conteúdo
type .env | findstr OPENAI_API_KEY

# 3. Obter nova chave em: https://platform.openai.com/api-keys

# 4. Atualizar .env
notepad .env

# 5. Reiniciar API
# Ctrl+C e rodar novamente
```

### "RateLimitError: You exceeded your current quota"
**Causa:** Limite de uso da API atingido.

**Solução:**
```powershell
# Verificar uso em: https://platform.openai.com/usage

# Adicionar créditos ou aguardar reset mensal
# Ou usar modelo mais barato:
OPENAI_CHAT_MODEL=gpt-3.5-turbo
```

### "OpenAI API timeout"
**Causa:** Rede lenta ou API sobrecarregada.

**Solução:**
```powershell
# Testar conexão
curl https://api.openai.com/v1/models -H "Authorization: Bearer $env:OPENAI_API_KEY"

# Verificar proxy/firewall
# Adicionar timeout maior (em embeddings.py ou pipeline.py)
```

## 📡 Problemas com API

### "Address already in use" (porta 8000)
**Solução:**
```powershell
# Verificar processo na porta
netstat -ano | findstr 8000

# Matar processo (substitua PID)
taskkill /F /PID 12345

# Ou usar outra porta
uvicorn packages.api.app.main:app --port 8001
```

### API inicia mas /docs não carrega
**Solução:**
```powershell
# Verificar se API está respondendo
curl http://localhost:8000/health

# Limpar cache do navegador (Ctrl+Shift+Del)

# Ou acessar em navegador anônimo
```

### "Internal Server Error" ao chamar /chat
**Solução:**
```powershell
# Ver logs da API (onde uvicorn está rodando)
# Verificar erro específico

# Problemas comuns:
# 1. OPENAI_API_KEY não configurado
# 2. Redis offline (mas deveria entrar em fallback)
# 3. Modelo inválido

# Testar health primeiro
curl http://localhost:8000/health
```

### CORS error no frontend
**Solução:**
```powershell
# Adicionar origem do frontend no .env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Reiniciar API
```

## 📦 Problemas com Ingestão

### "Redis não conectado" ao rodar load_json
**Solução:**
```powershell
# Verificar se Redis está rodando
docker ps | findstr redis

# Se não, subir Redis
docker compose up -d

# Aguardar e testar
timeout /t 5
python -m packages.ingest.app.load_json
```

### "Nenhum arquivo JSON encontrado"
**Causa:** Pasta samples não encontrada ou vazia.

**Solução:**
```powershell
# Verificar estrutura
dir packages\ingest\data\samples\

# Deve ter: sample_01.json, sample_02.json, sample_03.json

# Se não, criar ou baixar samples
```

### Embeddings não são gerados
**Solução:**
```powershell
# 1. Verificar se artigos foram carregados
python -m packages.ingest.app.load_json

# 2. Verificar OPENAI_API_KEY
type .env | findstr OPENAI_API_KEY

# 3. Rodar com logs detalhados
python -m packages.ingest.app.make_embeddings

# 4. Verificar se embeddings foram salvos
# No Redis Insight (http://localhost:8001)
# Ou via CLI:
docker exec spaceapss-redis redis-cli JSON.GET article:art-001 $.embedding
```

## 🧪 Problemas com Testes

### "No module named 'pytest'"
**Solução:**
```powershell
# Instalar dev dependencies
pip install -e ".[dev]"

# Verificar
pytest --version
```

### Testes falham com import errors
**Solução:**
```powershell
# Garantir que está na raiz do projeto
cd C:\Users\jotam\Documentos\GitHub\spaceapss-Mugiwaras\agents

# Reinstalar em modo editable
pip install -e .

# Rodar testes
pytest -v
```

### Testes de retriever falham
**Causa:** Mocks não configurados corretamente.

**Solução:**
```powershell
# Rodar apenas teste específico com verbose
pytest packages/api/tests/test_retriever.py -v -s

# Verificar imports
python -c "from packages.api.app.agent.retriever import Retriever; print('OK')"
```

## 🎯 Problemas com Busca/Retrieval

### Busca retorna resultados vazios
**Solução:**
```powershell
# 1. Verificar se artigos têm embeddings
curl http://localhost:8000/article/art-001

# 2. Verificar índice no Redis
docker exec spaceapss-redis redis-cli FT.INFO idx:articles

# 3. Forçar recriação de embeddings
python -m packages.ingest.app.make_embeddings

# 4. Testar busca direta
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"microgravity\"}"
```

### Resultados irrelevantes
**Causa:** Embeddings ou ranking não otimizados.

**Solução:**
```python
# Ajustar pesos em ranker.py:
# alpha=0.7  # peso vetorial (aumentar para mais semântico)
# alpha=0.5  # peso vetorial (diminuir para mais textual)

# Ajustar year_weight em ranker.py:
# year_weight=0.1  # bônus por ano recente
```

## 🔄 Modo Fallback

### Fallback não funciona
**Solução:**
```powershell
# 1. Verificar se samples existem
dir packages\ingest\data\samples\

# 2. Verificar logs da API ao iniciar
# Deve mostrar: "Retriever iniciado em modo FALLBACK"

# 3. Testar health
curl http://localhost:8000/health
# Esperado: "redis": "disconnected (fallback mode)"
```

### Fallback lento
**Causa:** Geração de embeddings on-the-fly.

**Solução:**
```python
# Pré-gerar embeddings nos samples (adicionar campo "embedding")
# Ou usar cache (implementar em retriever.py)
```

## 🐛 Debug Geral

### Ativar logs detalhados
```python
# Em logger.py, mudar nível:
logging.basicConfig(
    level=logging.DEBUG,  # Era INFO
    ...
)
```

### Testar componentes individualmente
```powershell
# Testar Redis
python -c "
from packages.api.app.services.redis_client import get_redis_client
redis = get_redis_client()
print(f'Conectado: {redis.is_connected()}')
"

# Testar Embeddings
python -c "
from packages.api.app.services.embeddings import get_embeddings_service
emb = get_embeddings_service()
vec = emb.get_embedding('test')
print(f'Embedding: {len(vec)} dims')
"

# Testar Retriever
python -c "
from packages.api.app.agent.retriever import get_retriever
ret = get_retriever()
docs = ret.retrieve('microgravity', top_k=3)
print(f'Docs: {len(docs)}')
"
```

## 📞 Suporte

### Logs úteis para debugging:
```powershell
# Logs da API
# (visível no terminal onde uvicorn está rodando)

# Logs do Redis
docker compose logs redis

# Logs do Docker
docker compose logs
```

### Informações para reportar bugs:
1. Sistema operacional e versão
2. Versão do Python (`python --version`)
3. Versão do Docker (`docker --version`)
4. Mensagem de erro completa
5. Passos para reproduzir
6. Logs relevantes

### Recursos:
- **README.md** - Documentação principal
- **QUICKSTART.md** - Guia rápido
- **API_EXAMPLES.md** - Exemplos de uso
- **ENV_VARS.md** - Variáveis de ambiente
- **ARCHITECTURE.md** - Arquitetura do sistema

## 🔄 Reset Completo

Se nada funcionar, reset completo:

```powershell
# 1. Parar tudo
docker compose down -v

# 2. Limpar Python cache
Remove-Item -Recurse -Force packages\**\__pycache__

# 3. Remover virtual env (se existir)
Remove-Item -Recurse -Force venv

# 4. Criar novo venv
python -m venv venv
.\venv\Scripts\activate

# 5. Reinstalar tudo
pip install --upgrade pip
pip install -e ".[dev]"

# 6. Subir Redis novamente
docker compose up -d

# 7. Ingerir dados
python -m packages.ingest.app.load_json
python -m packages.ingest.app.make_embeddings

# 8. Testar
pytest
uvicorn packages.api.app.main:app --reload
```

Isso deve resolver 99% dos problemas! 🚀
