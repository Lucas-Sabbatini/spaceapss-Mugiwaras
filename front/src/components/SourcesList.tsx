import type { Source } from '../types';

interface SourcesListProps {
  sources: Source[];
  onSourceClick: (articleId: string) => void;
}

export function SourcesList({ sources, onSourceClick }: SourcesListProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <p className="text-xs text-gray-600 font-medium">📚 Sources</p>
        <span className="text-xs text-gray-500 italic">(click to view citation)</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {sources.map((source) => (
          <button
            key={source.id}
            onClick={() => onSourceClick(source.id)}
            className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-full text-sm text-blue-700 transition-colors hover:shadow-sm group"
            title={`Click to view full citation: ${source.title}`}
          >
            <span className="text-blue-500 group-hover:text-blue-600">📄</span>
            <span className="font-medium">{source.title}</span>
            {source.year && (
              <span className="text-xs text-blue-600">({source.year})</span>
            )}
            {source.score !== undefined && source.score > 0 && (
              <span className="text-xs bg-blue-200 px-1.5 py-0.5 rounded">
                {(source.score * 100).toFixed(0)}%
              </span>
            )}
            <span className="text-xs text-blue-500 group-hover:text-blue-700 opacity-0 group-hover:opacity-100 transition-opacity">
              View →
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
