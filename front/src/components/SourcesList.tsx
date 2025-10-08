import type { Source } from '../types';

interface SourcesListProps {
  sources: Source[];
  onSourceClick: (articleId: string) => void;
}

export function SourcesList({ sources, onSourceClick }: SourcesListProps) {
  return (
    <div className="space-y-1">
      <p className="text-xs text-gray-600 font-medium mb-2">📚 Sources:</p>
      <div className="flex flex-wrap gap-2">
        {sources.map((source) => (
          <button
            key={source.id}
            onClick={() => onSourceClick(source.id)}
            className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-full text-sm text-blue-700 transition-colors"
          >
            <span className="font-medium">{source.title}</span>
            {source.year && (
              <span className="text-xs text-blue-600">({source.year})</span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
