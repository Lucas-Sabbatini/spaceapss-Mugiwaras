# 🚀 SpaceAPSS - Guia Rápido de Uso

## Frontend + Backend Integrados

### 📦 Estrutura do Projeto

```
spaceapss-Mugiwaras/
├── agents/           # Backend (FastAPI + Gemini + Redis)
│   ├── packages/
│   ├── .env
│   └── ...
└── front/            # Frontend (React + Vite + Tailwind)
    ├── src/
    ├── .env
    └── ...
```

## � Rodando no GitHub Codespaces

### URLs Públicas (Codespaces)
- **Backend:** https://humble-halibut-rvx7r4q7g6357j4-8000.app.github.dev
- **Frontend:** https://humble-halibut-rvx7r4q7g6357j4-5173.app.github.dev

> 💡 O Codespaces cria URLs públicas automaticamente com port forwarding!

## �🏃 Como Executar

### 1. Backend (Terminal 1)

```bash
cd /workspaces/spaceapss-Mugiwaras/agents

# Ativar virtualenv
source .venv/bin/activate

# Iniciar servidor (IMPORTANTE: usar 0.0.0.0 para Codespaces!)
uvicorn packages.api.app.main:app --host 0.0.0.0 --port 8000

# Ou em background:
uvicorn packages.api.app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
```

Verificar saúde: https://humble-halibut-rvx7r4q7g6357j4-8000.app.github.dev/health

### 2. Frontend (Terminal 2)

```bash
cd /workspaces/spaceapss-Mugiwaras/front

# Instalar dependências (primeira vez)
npm install

# Iniciar dev server
npm run dev
```

**Importante:** O comando `npm run dev` precisa ser executado de dentro da pasta `front/`!

Acessar: https://humble-halibut-rvx7r4q7g6357j4-5173.app.github.dev

> 💡 **Dica:** O Codespaces vai mostrar um popup com o link quando a porta 5173 estiver pronta. Clique em "Open in Browser"!

## ✅ Checklist de Funcionamento

- [ ] Backend rodando em https://humble-halibut-rvx7r4q7g6357j4-8000.app.github.dev
- [ ] Health check retorna `{"status":"ok"}`
- [ ] Frontend rodando em https://humble-halibut-rvx7r4q7g6357j4-5173.app.github.dev
- [ ] CORS configurado com URLs do Codespaces no `.env` do backend
- [ ] Redis conectado (ou modo fallback ativo)
- [ ] Portas públicas (visibility: Public) no painel de Ports do Codespaces

## 🎯 Testando o Sistema

### Via Frontend (Browser)
1. Abra https://humble-halibut-rvx7r4q7g6357j4-5173.app.github.dev
2. Digite uma pergunta: "Quais efeitos da microgravidade?"
3. Aguarde a resposta
4. Clique em uma fonte para ver o artigo completo

### Via API (curl)
```bash
curl -X POST https://humble-halibut-rvx7r4q7g6357j4-8000.app.github.dev/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"Quais efeitos da microgravidade?","topK":3}'
```

## 🛠️ Comandos Úteis

### Parar Processos

```bash
# Backend
pkill -f 'uvicorn packages.api.app.main:app'

# Frontend
# Pressionar Ctrl+C no terminal onde está rodando
# Ou:
lsof -ti:5173 | xargs kill -9
lsof -ti:5174 | xargs kill -9
```

### Verificar Logs

```bash
# Backend
tail -f /tmp/backend.log

# Frontend
tail -f /tmp/frontend.log
```

### Build para Produção (Frontend)

```bash
cd /workspaces/spaceapss-Mugiwaras/front
npm run build
npm run preview  # Preview do build
```

## 🔧 Troubleshooting

### "Network error" no frontend
- Verificar se backend está rodando
- Confirmar URL no `.env` do front: `VITE_API_URL=https://humble-halibut-rvx7r4q7g6357j4-8000.app.github.dev`
- Verificar CORS no backend
- **IMPORTANTE:** Verificar se as portas estão com visibility "Public" no painel de Ports

### "CORS policy" error
- Adicionar as URLs do Codespaces em `CORS_ORIGINS` no `.env` do backend
- Reiniciar backend
- Formato: `https://<codespace-name>-<port>.app.github.dev`

### Backend não conecta ao Redis
- O sistema funciona em modo fallback (sem Redis)
- Verificar `REDIS_URL` no `.env` se quiser usar Redis remoto

### Frontend mostra página em branco
- Verificar console do browser (F12)
- Confirmar que `npm install` foi executado
- Tentar `npm run build` e corrigir erros de TypeScript

## 📱 Funcionalidades Implementadas

### Chat
- ✅ Input de pergunta com Enter para enviar
- ✅ Shift+Enter para nova linha
- ✅ Histórico de mensagens
- ✅ Loading state durante processamento
- ✅ Tratamento de erros

### Fontes
- ✅ Chips clicáveis com título e ano
- ✅ Score de relevância (percentual)
- ✅ Abertura de modal ao clicar

### Modal de Artigo
- ✅ Título, autores, ano, DOI
- ✅ Abstract completo
- ✅ Seções com accordion (expandir/recolher)
- ✅ Lista de referências
- ✅ Metadados (keywords, journal, impact factor)
- ✅ Botões:
  - Copiar citação
  - Copiar DOI
  - Abrir URL (se disponível)
- ✅ Scroll interno
- ✅ Fechar clicando fora ou no X

## 🎨 Design

- Interface limpa e profissional
- Responsivo (desktop e mobile)
- Tailwind CSS para estilização
- Estados visuais claros (loading, erro, sucesso)

## 📝 Próximos Passos (Opcional)

- [ ] Persistência de histórico (localStorage ou backend)
- [ ] Dark mode
- [ ] Export de conversas (PDF/Markdown)
- [ ] Feedback sobre respostas (útil/não útil)
- [ ] Sugestões de perguntas
- [ ] Busca em histórico
