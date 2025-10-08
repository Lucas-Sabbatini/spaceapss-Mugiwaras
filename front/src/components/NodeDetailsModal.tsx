import type { NodeDetails } from '../types';

interface NodeDetailsModalProps {
  nodeDetails: NodeDetails | null;
  isOpen: boolean;
  onClose: () => void;
  isLoading?: boolean;
  error?: string | null;
}

export function NodeDetailsModal({ nodeDetails, isOpen, onClose, isLoading, error }: NodeDetailsModalProps) {
  if (!isOpen) return null;

  const getTypeLabel = (type: string): string => {
    return type.charAt(0).toUpperCase() + type.slice(1);
  };

  const getTypeColor = (type: string): string => {
    const colors: Record<string, string> = {
      author: 'bg-blue-100 text-blue-800 border-blue-200',
      institution: 'bg-green-100 text-green-800 border-green-200',
      organism: 'bg-amber-100 text-amber-800 border-amber-200',
      journal: 'bg-purple-100 text-purple-800 border-purple-200',
    };
    return colors[type] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[80vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-start justify-between">
          {isLoading ? (
            <div className="flex-1">
              <div className="animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ) : error ? (
            <div className="flex-1">
              <h2 className="text-xl font-bold text-red-600">Error loading node details</h2>
              <p className="text-sm text-red-500 mt-1">{error}</p>
            </div>
          ) : nodeDetails ? (
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getTypeColor(nodeDetails.attributes.type)}`}>
                  {getTypeLabel(nodeDetails.attributes.type)}
                </span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900">{nodeDetails.attributes.name}</h2>
              <div className="flex gap-4 mt-2 text-sm text-gray-600">
                <span>🔗 {nodeDetails.degree} connections</span>
                <span>📄 {nodeDetails.attributes.experiment_ids.length} experiments</span>
              </div>
            </div>
          ) : null}
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-light ml-4"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading node details...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <p className="text-red-600 mb-2">❌ {error}</p>
                <p className="text-sm text-gray-500">Could not load node information.</p>
              </div>
            </div>
          ) : nodeDetails ? (
            <div className="space-y-6">
              {/* Experiments Links */}
              {nodeDetails.attributes.experiment_ids.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    📄 Associated Experiments
                    <span className="text-sm font-normal text-gray-500">
                      ({nodeDetails.attributes.experiment_ids.length})
                    </span>
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-96 overflow-y-auto">
                    {nodeDetails.attributes.experiment_ids.map((expId) => (
                      <a
                        key={expId}
                        href={`https://www.ncbi.nlm.nih.gov/pmc/articles/${expId}/`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-3 py-2 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors group"
                      >
                        <span className="text-blue-700 font-mono text-sm">{expId}</span>
                        <svg
                          className="w-4 h-4 text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                          />
                        </svg>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {/* Neighbors Info */}
              {nodeDetails.neighbors && nodeDetails.neighbors.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    🕸️ Connected Nodes
                    <span className="text-sm font-normal text-gray-500">
                      ({nodeDetails.neighbors_count})
                    </span>
                  </h3>
                  <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                    <div className="flex flex-wrap gap-2">
                      {nodeDetails.neighbors.slice(0, 50).map((neighbor, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-white border border-gray-300 rounded text-xs text-gray-700"
                        >
                          {neighbor.replace(/^(author|institution|organism|journal):/, '')}
                        </span>
                      ))}
                      {nodeDetails.neighbors.length > 50 && (
                        <span className="px-2 py-1 text-xs text-gray-500 italic">
                          ... and {nodeDetails.neighbors.length - 50} more
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
