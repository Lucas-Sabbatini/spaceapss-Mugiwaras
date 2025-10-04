# 📚 Índice de Documentação

Bem-vindo ao repositório **SpaceAPSS Agents**! Este índice ajuda você a navegar pela documentação.

## 🚀 Começar Rápido

1. **[QUICKSTART.md](QUICKSTART.md)** - Guia rápido de 5 minutos para rodar o projeto
   - Instalar dependências
   - Configurar .env
   - Subir Redis
   - Ingerir dados
   - Iniciar API

## 📖 Documentação Principal

2. **[README.md](README.md)** - Documentação completa do projeto
   - Visão geral da stack
   - Estrutura de pastas detalhada
   - Fluxo do agente
   - Comandos Makefile
   - Instruções de desenvolvimento

## 🏗️ Arquitetura e Design

3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitetura do sistema
   - Diagramas de fluxo
   - Componentes e camadas
   - Decisões de arquitetura
   - Tecnologias por componente
   - Estratégias de escalabilidade

## 💡 Exemplos Práticos

4. **[API_EXAMPLES.md](API_EXAMPLES.md)** - Exemplos de uso da API
   - Requisições cURL
   - Exemplos em Python
   - Exemplos em JavaScript
   - Casos de uso diversos
   - Tratamento de erros

## 🔐 Configuração

5. **[ENV_VARS.md](ENV_VARS.md)** - Variáveis de ambiente
   - Todas as variáveis suportadas
   - Exemplos de configuração
   - Modelos OpenAI disponíveis
   - Boas práticas de segurança
   - Validação e testes

## 🔧 Solução de Problemas

6. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Guia de troubleshooting
   - Problemas comuns e soluções
   - Debug de componentes
   - Reset completo do sistema
   - Informações para reportar bugs

## 📝 Resumo da Implementação

7. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Resumo executivo
   - Status da implementação
   - Funcionalidades implementadas
   - Critérios de aceite cumpridos
   - Diferenciais do projeto
   - Próximos passos

## 📄 Arquivos de Configuração

### Desenvolvimento
- **[.env.example](.env.example)** - Template de variáveis de ambiente
- **[docker-compose.yml](docker-compose.yml)** - Configuração do Redis Stack
- **[pyproject.toml](pyproject.toml)** - Dependências e configuração Python
- **[Makefile](Makefile)** - Atalhos de comandos úteis
- **[.gitignore](.gitignore)** - Arquivos ignorados pelo Git

## 📦 Código Fonte

### API (packages/api/app/)
- **main.py** - Aplicação FastAPI principal
- **config.py** - Configurações (Pydantic Settings)
- **schemas.py** - Modelos Pydantic (Article, ChatRequest, etc)
- **deps.py** - Dependências injetáveis

#### Routers (packages/api/app/routers/)
- **health.py** - Health check endpoint
- **chat.py** - Chat/perguntas endpoint
- **articles.py** - CRUD de artigos

#### Agent (packages/api/app/agent/)
- **pipeline.py** - Orquestração do agente
- **retriever.py** - Busca híbrida (vetorial + textual)
- **ranker.py** - Re-ranking de documentos
- **prompts.py** - Templates de prompts

#### Services (packages/api/app/services/)
- **redis_client.py** - Cliente Redis + RediSearch
- **embeddings.py** - Wrapper OpenAI/Azure
- **logger.py** - Logging estruturado

### Ingestão (packages/ingest/app/)
- **load_json.py** - Carrega artigos no Redis
- **make_embeddings.py** - Gera embeddings
- **utils.py** - Utilitários de ingestão

### Testes (packages/api/tests/)
- **test_schemas.py** - Testes de validação Pydantic
- **test_retriever.py** - Testes do retriever
- **conftest.py** - Fixtures pytest

### Dados (packages/ingest/data/samples/)
- **sample_01.json** - Microgravidade e células-tronco
- **sample_02.json** - Proteção contra radiação espacial
- **sample_03.json** - Adaptações cardiovasculares

## 🎯 Fluxo de Leitura Recomendado

### Para Desenvolvedores Novos
1. [QUICKSTART.md](QUICKSTART.md) - Configure o ambiente
2. [README.md](README.md) - Entenda o projeto
3. [API_EXAMPLES.md](API_EXAMPLES.md) - Teste a API
4. [ARCHITECTURE.md](ARCHITECTURE.md) - Estude a arquitetura
5. Explore o código fonte

### Para DevOps/SRE
1. [README.md](README.md) - Visão geral
2. [ENV_VARS.md](ENV_VARS.md) - Configurações
3. [ARCHITECTURE.md](ARCHITECTURE.md) - Infraestrutura
4. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problemas comuns
5. docker-compose.yml - Deploy

### Para Product Managers
1. [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Status
2. [README.md](README.md) - Funcionalidades
3. [API_EXAMPLES.md](API_EXAMPLES.md) - Casos de uso
4. [ARCHITECTURE.md](ARCHITECTURE.md) - Escalabilidade

### Para QA/Testers
1. [QUICKSTART.md](QUICKSTART.md) - Setup
2. [API_EXAMPLES.md](API_EXAMPLES.md) - Casos de teste
3. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Cenários de erro
4. packages/api/tests/ - Testes automatizados

## 🔍 Busca Rápida

### Como fazer...?
- **Instalar** → [QUICKSTART.md](QUICKSTART.md)
- **Configurar variáveis** → [ENV_VARS.md](ENV_VARS.md)
- **Fazer requisições** → [API_EXAMPLES.md](API_EXAMPLES.md)
- **Entender a arquitetura** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **Resolver erros** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Onde está...?
- **Código da API** → packages/api/app/
- **Código do agente** → packages/api/app/agent/
- **Scripts de ingestão** → packages/ingest/app/
- **Testes** → packages/api/tests/
- **Samples** → packages/ingest/data/samples/

## 📞 Suporte

Se ainda tiver dúvidas:
1. Verifique [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Revise a documentação relevante
3. Verifique os logs da aplicação
4. Abra uma issue no GitHub

## 🎉 Contribuindo

Este projeto segue boas práticas de código:
- ✅ Tipagem completa (Pydantic v2)
- ✅ Logs estruturados
- ✅ Testes automatizados (pytest)
- ✅ Formatação (black)
- ✅ Lint (ruff)
- ✅ Documentação completa

Para contribuir:
1. Leia [README.md](README.md)
2. Configure o ambiente com [QUICKSTART.md](QUICKSTART.md)
3. Estude [ARCHITECTURE.md](ARCHITECTURE.md)
4. Siga os padrões existentes
5. Adicione testes
6. Atualize a documentação

## 📊 Status do Projeto

✅ **100% Completo e Funcional**

Veja [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) para detalhes.

---

**Última atualização:** 2025-01-04
**Versão:** 0.1.0
**Licença:** MIT
