# Visão Geral

Este projeto surge como a contribuição do nosso time Mugiwaras, para o hackaton Nasa Space Apps.

Nossa tarefa era era construir uma aplicação web funcional que utilizasse IA para resumir as 608 publicações da NASA em biosciências listadas em um repositório online (veja a aba Resources) e que permitisse a você explorar os impactos e resultados dos experimentos descritos nessas publicações.

O projeto permite que usuários façam perguntas em linguagem natural e recebam respostas contextualizadas baseadas em uma base de dados de artigos científicos do PubMed/PMC sobre medicina espacial, microbiologia, efeitos da microgravidade, e outros tópicos relacionados.

- **Dados de entrada:** Um CSV contendo links para 608 artigos sobre biologia espacial.

- **Saída:** Essa aplicação web, que implementa um chatbot, juntamente com uma engine de visualização do grafo de conhecimento, construído com base nos artigos.

---

## Arquitetura do Sistema

![Diagrama do Projeto](./img/Diagrama%20de%20caso%20de%20uso.png)

### Stack Tecnológico

#### **Backend (agents/)**
- **FastAPI** - Framework web assíncrono
- **MongoDB** - Banco de dados não relacional/vetorial para embeddings e estruturação dos dados extraídos.
- **Google Gemini 2.0 Flash** - LLM para geração de respostas
- **Text Embedding 004** - Modelo de embeddings do Google
- **NCBI E-utilities API** - Busca de artigos científicos

#### **Frontend (front/)**
- **React + TypeScript** - Interface do usuário
- **Vite** - Build tool e dev server
- **TailwindCSS** - Estilização
- **Axios** - Cliente HTTP
- **Vis.js** - Visualização dos grafos no front.



## Segurança e Configuração

### Variáveis de Ambiente (`.env`)
```bash
GOOGLE_API_KEY=
GOOGLE_EMBED_MODEL=models/text-embedding-004
GOOGLE_CHAT_MODEL=gemini-2.0-flash
GCP_PROJECT_ID=
GCP_REGION=us-central1

MONGODB_URI=
MONGODB_DATABASE=spaceapss
MONGODB_COLLECTION=articles

API_PORT=
ENV=
CORS_ORIGINS=
FETCH_TIMEOUT_SECS=
```

### Variáveis de Ambiente Front-End (`.env`)
```bash
VITE_API_URL=http://localhost:8000
```
---

## Fluxo de Desenvolvimento

### Setup Inicial
#### Backend
```bash
cd agents
docker compose up --build
```

#### Processamento Inicial dos Artigos
```bash
# Processar os 608 artigos do CSV (~30-60 min)
# Deve ser rodado antes da fase acima
python process_batch.py
```


#### Frontend
```bash
cd front
docker compose up --build
```

### Adicionar Novos Artigos

1. **Atualizar o CSV** em `shared/SB_publication_PMC.csv`
2. **Executar o processamento:**
  ```bash
  cd agents
  python process_batch.py
  python create_graph.py
  ```
3. **Reiniciar a API** (se estiver rodando)

---

**Nota:** Certifique-se de que todos os scripts estão no diretório `agents/` e que as variáveis de ambiente estão configuradas corretamente no arquivo `.env` antes de executar os comandos.

