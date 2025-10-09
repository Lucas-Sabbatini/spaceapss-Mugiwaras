# SpaceAPSS Frontend

Interface web para interagir com o agente de pesquisa científica SpaceAPSS.

## Tecnologias

- **React 18** + **TypeScript**
- **Vite** (build tool e dev server)
- **Tailwind CSS** (estilização)
- **vis.js** (visualização de Knowledge Graph)
- **React Markdown** (renderização de markdown)

## Pré-requisitos

- Node.js 18+ ou superior
- Docker e Docker Compose (para executar com containers)
- Backend da API rodando em `http://localhost:8000`

## Instalação

### Método 1: Desenvolvimento Local

```bash
# Instalar dependências
npm install

# Copiar arquivo de ambiente
cp .env.example .env

# Editar .env se necessário (ajustar URL da API)
# VITE_API_URL=http://localhost:8000
```

### Método 2: Docker

Não é necessário instalar dependências. Pule para a seção "Executando com Docker".

## Executando

### Desenvolvimento Local

```bash
# Modo desenvolvimento com hot reload
npm run dev

# Build para produção
npm run build

# Preview do build de produção
npm run preview
```

A aplicação estará disponível em `http://localhost:5173`

### Executando com Docker

**Apenas Frontend:**

```bash
# Build e start do container
docker build -t spaceapss-frontend .
docker run -p 3000:80 -e VITE_API_URL=http://localhost:8000 spaceapss-frontend
```

A aplicação estará disponível em `http://localhost:3000`

**Frontend + Backend (stack completa):**

```bash
# Na pasta front/, executar docker-compose
docker compose up --build

# Ou em modo detached (background)
docker compose up -d --build
```

Serviços disponíveis:
- **Frontend:** `http://localhost:3000`
- **Backend API:** `http://localhost:8000`
- **API Docs:** `http://localhost:8000/docs`

**Parar containers:**

```bash
# Parar e remover containers
docker compose down

# Parar, remover containers e volumes
docker compose down -v
```

## Funcionalidades

### Chat Interativo com RAG
- Campo de texto para fazer perguntas sobre artigos científicos
- Histórico de conversas em tempo real
- Respostas contextualizadas usando Retrieval-Augmented Generation
- Loading states durante processamento
- Tratamento de erros com mensagens amigáveis

### Visualização de Knowledge Graph
- Grafo interativo de entidades (autores, instituições, organismos, termos MeSH)
- Expansão dinâmica de nós para explorar relacionamentos
- Filtragem por experimento
- Detalhes de nós com metadados
- Estatísticas do grafo (número de nós, arestas, distribuição de tipos)

### Exibição de Fontes
- Chips clicáveis com as fontes dos artigos citados
- Score de relevância para cada fonte
- Ano de publicação e metadados
- Link direto para artigos no PubMed Central

### Modal de Artigo
- Visualização completa de artigos científicos
- Seções estruturadas com accordion (abstract, introduction, methods, results, etc.)
- Lista de referências bibliográficas
- Metadados completos (palavras-chave, journal, DOI, autores, afiliações)
- Entidades extraídas (organismos, instituições, termos MeSH)
- Botões de ação:
  - Copiar citação formatada
  - Copiar DOI
  - Abrir artigo no PMC (PubMed Central)

## Interface

- Design limpo e responsivo com Tailwind CSS
- Otimizado para desktop e mobile
- Modo claro com paleta de cores consistente
- Atalhos de teclado:
  - `Enter`: Enviar mensagem no chat
  - `Shift+Enter`: Nova linha no campo de texto
  - `ESC`: Fechar modais

## Integração com Backend

A aplicação espera que o backend esteja rodando e disponível na URL configurada em `.env` (padrão: `http://localhost:8000`).

### Endpoints Utilizados

**Chat RAG:**
- `POST /api/chat/query` - Enviar pergunta e receber resposta contextualizada

**Knowledge Graph:**
- `GET /api/graph/{experiment_id}` - Obter subgrafo de um experimento
- `GET /api/graph/neighbors/{node_id}` - Obter vizinhos de um nó (com filtro `no_experiment_id`)

**Artigos:**
- `GET /api/articles` - Listar artigos com paginação
- `GET /api/articles/{pmcid}` - Obter detalhes completos de um artigo

**Health Check:**
- `GET /health` - Verificar status do backend e dependências

### Configuração CORS

Certifique-se de que o backend permite requisições das seguintes origens nas configurações de CORS:
- `http://localhost:5173` (desenvolvimento local)
- `http://localhost:3000` (Docker)

No arquivo `.env` do backend, adicione:
```bash
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Estrutura do Projeto

```
src/
├── components/              # Componentes React
│   ├── ChatBox.tsx         # Componente principal do chat
│   ├── MessageBubble.tsx   # Bolha de mensagem (usuário/assistente)
│   ├── SourcesList.tsx     # Lista de fontes citadas
│   ├── ArticleModal.tsx    # Modal de artigo (deprecated)
│   ├── ArticleDetailModal.tsx  # Modal detalhado de artigo
│   ├── GraphViewer.tsx     # Container do Knowledge Graph
│   ├── GraphVisualization.tsx  # Visualização vis.js do grafo
│   ├── NodeDetailsModal.tsx    # Detalhes de nós do grafo
│   ├── GraphStatsView.tsx  # Estatísticas do grafo
│   ├── ImageViewer.tsx     # Visualizador de imagens do grafo
│   └── MarkdownContent.tsx # Renderizador de markdown
├── lib/
│   └── api.ts              # Cliente da API (fetch wrapper)
├── types.ts                # Tipos TypeScript compartilhados
├── index.css               # Estilos globais + Tailwind
├── App.tsx                 # Componente raiz da aplicação
└── main.tsx                # Entry point do React

public/
└── graphs/                 # Imagens estáticas do Knowledge Graph
```

## Arquitetura Docker

### Dockerfile Multi-Stage

O Dockerfile usa uma estratégia multi-stage para otimizar o tamanho da imagem final:

1. **Stage 1 (Build):** Compila a aplicação React com Vite
   - Instala dependências com npm
   - Executa `npm run build` para gerar assets otimizados

2. **Stage 2 (Production):** Serve a aplicação com Nginx
   - Copia apenas os arquivos buildados (`dist/`)
   - Usa imagem Alpine (menor tamanho)
   - Configuração customizada do Nginx

### Nginx Configuration

O arquivo `nginx.conf` inclui:
- Compressão Gzip para assets
- Cache de arquivos estáticos (1 ano)
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- SPA routing (todas as rotas redirecionam para `index.html`)
- Health check endpoint em `/health`

### Docker Compose

O `docker-compose.yaml` orquestra frontend e backend:
- **Network isolada:** `spaceapss-network` para comunicação entre containers
- **Dependências:** Frontend depende do backend
- **Environment variables:** Configuração da URL da API
- **Volume mounting:** Compartilha arquivos do Knowledge Graph entre containers

## Troubleshooting

### Backend não conecta

Verifique se:
1. O backend está rodando em `http://localhost:8000`
2. O CORS está configurado corretamente no backend (ver seção "Integração com Backend")
3. A variável `VITE_API_URL` no `.env` está correta
4. Não há firewall bloqueando a porta 8000

**Teste a conexão:**
```bash
curl http://localhost:8000/health
```

### Erro ao carregar artigo

- Verifique se o backend retorna o objeto `article` completo na resposta
- Confirme que os PMCIDs dos artigos estão corretos
- Verifique os logs do console do navegador (F12)
- Teste o endpoint diretamente: `curl http://localhost:8000/api/articles/{pmcid}`

### Docker: Containers não iniciam

**Verificar logs:**
```bash
docker compose logs frontend
docker compose logs backend
```

**Reconstruir imagens:**
```bash
docker compose down
docker compose build --no-cache
docker compose up
```

**Verificar portas em uso:**
```bash
# Linux/Mac
lsof -i :3000
lsof -i :8000

# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :8000
```

### Docker: Frontend não conecta ao Backend

Se estiver usando Docker Compose, certifique-se de:
1. Ambos os containers estão na mesma network (`spaceapss-network`)
2. A variável `VITE_API_URL` aponta para o host correto
3. Se acessando de fora dos containers, use `http://localhost:8000`
4. Se comunicação interna, use `http://backend:8000`

### Erro: Module not found

**Desenvolvimento local:**
```bash
# Limpar cache e reinstalar
rm -rf node_modules package-lock.json
npm install
```

**Docker:**
```bash
# Reconstruir sem cache
docker compose build --no-cache frontend
```

### Performance lenta do Knowledge Graph

Se o grafo estiver lento com muitos nós:
1. Reduza o número de nós exibidos (filtrar por experimento)
2. Use a visualização compacta (compact view)
3. Desabilite animações no navegador
4. Aumente recursos do container Docker (CPU/RAM)

## Variáveis de Ambiente

| Variável | Descrição | Padrão | Obrigatório |
|----------|-----------|--------|-------------|
| `VITE_API_URL` | URL base da API backend | `http://localhost:8000` | Sim |

**Nota:** Variáveis `VITE_*` são injetadas em tempo de build pelo Vite. Se mudar o `.env`, é necessário rebuildar a aplicação.

## Notas

- As mensagens do chat não são persistidas (são perdidas ao recarregar a página)
- O modal de artigo pode ser fechado clicando fora dele, pressionando ESC ou no botão X
- Citações e DOIs são copiados para a área de transferência ao clicar nos botões
- O Knowledge Graph usa vis.js DataSet para atualizações incrementais sem reload
- A expansão de nós no grafo filtra automaticamente nós do mesmo experimento usando `no_experiment_id`

## Build de Produção

### Build Local

```bash
npm run build
```

Arquivos otimizados serão gerados em `dist/`:
- HTML, CSS e JS minificados
- Assets com hash para cache busting
- Source maps para debugging

### Build Docker

A imagem Docker usa multi-stage build automaticamente:
```bash
docker build -t spaceapss-frontend:latest .
```

Tamanho final da imagem: ~25-30 MB (nginx:alpine + assets buildados)

## Recursos Adicionais

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [vis.js Network](https://visjs.github.io/vis-network/)
- [React Markdown](https://github.com/remarkjs/react-markdown)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
