import type { Message } from '../types';
import { SourcesList } from './SourcesList';

interface MessageBubbleProps {
  message: Message;
  onSourceClick: (articleId: string) => void;
}

export function MessageBubble({ message, onSourceClick }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`px-4 py-3 rounded-lg ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-white border border-gray-200 text-gray-900'
          }`}
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2">
            <SourcesList sources={message.sources} onSourceClick={onSourceClick} />
          </div>
        )}

        <div className="mt-1 text-xs text-gray-500 px-1">
          {message.timestamp.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
}
