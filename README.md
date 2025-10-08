# Visão Geral

Este projeto surge como a contribuição do nosso time Mugiwaras, para o hackaton Nasa Space Apps.

Nossa tarefa era era construir uma aplicação web funcional que utilizasse IA para resumir as 608 publicações da NASA em biosciências listadas em um repositório online (veja a aba Resources) e que permitisse a você explorar os impactos e resultados dos experimentos descritos nessas publicações.

O projeto permite que usuários façam perguntas em linguagem natural e recebam respostas contextualizadas baseadas em uma base de dados de artigos científicos do PubMed/PMC sobre medicina espacial, microbiologia, efeitos da microgravidade, e outros tópicos relacionados.

- **Dados de entrada:** Um CSV contendo links para 608 artigos sobre biologia espacial.

- **Saída:** Essa aplicação web, que implementa um chatbot, juntamente com uma engine de visualização do grafo de conhecimento, construído com base nos artigos.

---

## Arquitetura do Sistema

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
