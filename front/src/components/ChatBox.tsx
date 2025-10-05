import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import type { Message, Article, ArticleDetail } from '../types';
import { sendChatMessage, getArticleDetail } from '../lib/api';
import { MessageBubble } from './MessageBubble';
import { ArticleModal } from './ArticleModal';
import { ArticleDetailModal } from './ArticleDetailModal';

export function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedArticleDetail, setSelectedArticleDetail] = useState<ArticleDetail | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
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
      setError(err instanceof Error ? err.message : 'Error querying the agent');
      
      // Add error message
      const errorMessage: Message = {
        role: 'agent',
        content: '❌ Error processing your question. Please try again.',
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

  const handleSourceClick = async (articleId: string) => {
    // Open details modal and fetch data from backend
    setIsDetailModalOpen(true);
    setIsLoadingDetail(true);
    setDetailError(null);
    setSelectedArticleDetail(null);

    try {
      const articleDetail = await getArticleDetail(articleId);
      setSelectedArticleDetail(articleDetail);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error loading article';
      setDetailError(errorMessage);
    } finally {
      setIsLoadingDetail(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-5xl mx-auto">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">SpaceAPSS Research Agent</h1>
        <p className="text-sm text-gray-600 mt-1">
          Ask about scientific articles on space medicine
        </p>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-12">
            <p className="text-lg mb-2">👋 Hello! How can I help you?</p>
            <p className="text-sm">Ask a question about scientific articles</p>
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
                <span className="text-sm text-gray-600">Processing...</span>
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
            placeholder="Type your question... (Enter to send, Shift+Enter for new line)"
            className="input-field"
            rows={2}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="btn-primary self-end"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
        <p className="text-xs text-gray-500 mt-2">
          Press <kbd className="px-1 py-0.5 bg-gray-100 rounded">Enter</kbd> to send or{' '}
          <kbd className="px-1 py-0.5 bg-gray-100 rounded">Shift+Enter</kbd> for new line
        </p>
      </div>

      {/* Article Modal (antigo - pode ser removido se não for mais usado) */}
      <ArticleModal
        article={selectedArticle}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedArticle(null);
        }}
      />

      {/* Article Detail Modal (novo - com dados enriquecidos do MongoDB) */}
      <ArticleDetailModal
        article={selectedArticleDetail}
        isOpen={isDetailModalOpen}
        isLoading={isLoadingDetail}
        error={detailError}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedArticleDetail(null);
          setDetailError(null);
        }}
      />
    </div>
  );
}
