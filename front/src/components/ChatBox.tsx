import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import type { Message, Article } from '../types';
import { sendChatMessage } from '../lib/api';
import { MessageBubble } from './MessageBubble';
import { ArticleModal } from './ArticleModal';

export function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    
    const question = input.trim();
    if (!question || isLoading) return;

    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: question,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setError(null);
    setIsLoading(true);

    try {
      const response = await sendChatMessage({ question, topK: 5 });

      // Add agent message
      const agentMessage: Message = {
        role: 'agent',
        content: response.answer,
        sources: response.sources,
        article: response.article,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, agentMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao consultar o agente');
      
      // Add error message
      const errorMessage: Message = {
        role: 'agent',
        content: '❌ Erro ao processar sua pergunta. Por favor, tente novamente.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSourceClick = (articleId: string) => {
    // Find the article in messages
    const messageWithArticle = messages.find(
      (msg) => msg.article && msg.article.id === articleId
    );
    
    if (messageWithArticle?.article) {
      setSelectedArticle(messageWithArticle.article);
      setIsModalOpen(true);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-5xl mx-auto">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">SpaceAPSS Research Agent</h1>
        <p className="text-sm text-gray-600 mt-1">
          Pergunte sobre artigos científicos de medicina espacial
        </p>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-12">
            <p className="text-lg mb-2">👋 Olá! Como posso ajudar?</p>
            <p className="text-sm">Faça uma pergunta sobre artigos científicos</p>
          </div>
        )}

        {messages.map((message, index) => (
          <MessageBubble
            key={index}
            message={message}
            onSourceClick={handleSourceClick}
          />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="animate-pulse flex gap-1">
                  <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animation-delay-200"></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animation-delay-400"></div>
                </div>
                <span className="text-sm text-gray-600">Processando...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Toast */}
      {error && (
        <div className="mx-6 mb-2 px-4 py-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-gray-200 bg-white px-6 py-4">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Digite sua pergunta... (Enter para enviar, Shift+Enter para nova linha)"
            className="input-field"
            rows={2}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="btn-primary self-end"
          >
            {isLoading ? 'Enviando...' : 'Enviar'}
          </button>
        </form>
        <p className="text-xs text-gray-500 mt-2">
          Pressione <kbd className="px-1 py-0.5 bg-gray-100 rounded">Enter</kbd> para enviar ou{' '}
          <kbd className="px-1 py-0.5 bg-gray-100 rounded">Shift+Enter</kbd> para nova linha
        </p>
      </div>

      {/* Article Modal */}
      <ArticleModal
        article={selectedArticle}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedArticle(null);
        }}
      />
    </div>
  );
}
