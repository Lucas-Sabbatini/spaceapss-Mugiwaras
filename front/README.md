# SpaceAPSS Frontend

Interface web para interagir com o agente de pesquisa científica SpaceAPSS.

## 🚀 Tecnologias

- **React 18** + **TypeScript**
- **Vite** (build tool)
- **Tailwind CSS** (estilização)

## 📋 Pré-requisitos

- Node.js 18+ ou superior
- Backend da API rodando em `http://localhost:8000`

## 🔧 Instalação

```bash
# Instalar dependências
npm install

# Copiar arquivo de ambiente
cp .env.example .env

# Editar .env se necessário (ajustar URL da API)
```

## 🏃 Executando

```bash
# Modo desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview
```

A aplicação estará disponível em `http://localhost:5173`

## 🎯 Funcionalidades

### Chat Interativo
- Campo de texto para fazer perguntas
- Histórico de conversas
- Loading states durante processamento
- Tratamento de erros amigável

### Exibição de Fontes
- Chips clicáveis com as fontes dos artigos
- Score de relevância (quando disponível)
- Ano de publicação

### Modal de Artigo
- Visualização completa do artigo científico
- Seções com accordion (expansível/recolhível)
- Lista de referências
- Metadados (palavras-chave, journal, etc.)
- Botões de ação:
  - Copiar citação
  - Copiar DOI
  - Abrir URL/PDF (quando disponível)

## 🎨 Interface

- Design limpo e responsivo
- Otimizado para desktop e mobile
- Atalhos de teclado:
  - `Enter`: Enviar mensagem
  - `Shift+Enter`: Nova linha

## 🔗 Integração com Backend

A aplicação espera que o backend esteja rodando e disponível na URL configurada em `.env` (padrão: `http://localhost:8000`).

### Endpoints utilizados:

- `POST /chat` - Enviar pergunta e receber resposta
- `GET /health` - Verificar status do backend

### CORS

Certifique-se de que o backend permite requisições de `http://localhost:5173` nas configurações de CORS.

## 📁 Estrutura do Projeto

```
src/
├── components/           # Componentes React
│   ├── ChatBox.tsx      # Componente principal do chat
│   ├── MessageBubble.tsx # Bolha de mensagem
│   ├── SourcesList.tsx  # Lista de fontes
│   └── ArticleModal.tsx # Modal de artigo
├── lib/
│   └── api.ts           # Cliente da API
├── types.ts             # Tipos TypeScript
├── index.css            # Estilos globais
├── App.tsx              # Componente raiz
└── main.tsx             # Entry point
```

## 🐛 Troubleshooting

### Backend não conecta
Verifique se:
1. O backend está rodando em `http://localhost:8000`
2. O CORS está configurado corretamente
3. A variável `VITE_API_URL` no `.env` está correta

### Erro ao carregar artigo
- Verifique se o backend retorna o objeto `article` completo na resposta
- Confirme que os IDs dos artigos estão corretos

## 📝 Notas

- As mensagens não são persistidas (são perdidas ao recarregar a página)
- O modal pode ser fechado clicando fora dele ou no botão X
- Citações e DOIs são copiados para a área de transferência ao clicar nos botões
