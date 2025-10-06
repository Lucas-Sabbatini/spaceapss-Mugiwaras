import { useState } from 'react';
import type { ArticleDetail } from '../types';

interface ArticleDetailModalProps {
  article: ArticleDetail | null;
  isOpen: boolean;
  onClose: () => void;
  isLoading?: boolean;
  error?: string | null;
}

export function ArticleDetailModal({ article, isOpen, onClose, isLoading, error }: ArticleDetailModalProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'fulltext'>('overview');

  if (!isOpen) return null;

  const copyCitation = () => {
    if (!article) return;
    const citation = `${article.authors.join(', ')} (${article.year}). ${article.title}. ${article.doi ? `DOI: ${article.doi}` : ''}`;
    navigator.clipboard.writeText(citation);
    alert('Citation copied!');
  };

  const copyDoi = () => {
    if (article?.doi) {
      navigator.clipboard.writeText(article.doi);
      alert('DOI copied!');
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-start justify-between sticky top-0 bg-white rounded-t-lg">
          {isLoading ? (
            <div className="flex-1">
              <div className="animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ) : error ? (
            <div className="flex-1">
              <h2 className="text-xl font-bold text-red-600">Error loading article</h2>
              <p className="text-sm text-red-500 mt-1">{error}</p>
            </div>
          ) : article ? (
            <div className="flex-1 pr-4">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">{article.title || 'No title'}</h2>
              <div className="flex flex-wrap items-center gap-2 text-sm text-gray-600">
                {article.authors.length > 0 && (
                  <span>{article.authors.slice(0, 3).join(', ')}{article.authors.length > 3 ? ' et al.' : ''}</span>
                )}
                {article.year && <span>• {article.year}</span>}
                {article.journal && <span>• {article.journal}</span>}
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                  {article.experiment_id}
                </span>
                {article.url && (
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-green-700 hover:text-green-800 hover:underline bg-green-50 hover:bg-green-100 px-2 py-1 rounded inline-flex items-center gap-1 transition-colors"
                  >
                    <span>🔗 View Article</span>
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                )}
                {article.doi && (
                  <a
                    href={`https://doi.org/${article.doi}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:underline bg-blue-50 px-2 py-1 rounded"
                  >
                    DOI: {article.doi}
                  </a>
                )}
                {article.pmid && (
                  <a
                    href={`https://pubmed.ncbi.nlm.nih.gov/${article.pmid}/`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:underline bg-blue-50 px-2 py-1 rounded"
                  >
                    PMID: {article.pmid}
                  </a>
                )}
              </div>
            </div>
          ) : null}
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-light"
          >
            ×
          </button>
        </div>

        {/* Tabs */}
        {!isLoading && !error && article && (
          <div className="px-6 py-2 border-b border-gray-200 bg-gray-50">
            <div className="flex gap-4">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-3 py-2 text-sm font-medium rounded-t transition-colors ${
                  activeTab === 'overview'
                    ? 'bg-white text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📋 Overview
              </button>
              {article.full_text && (
                <button
                  onClick={() => setActiveTab('fulltext')}
                  className={`px-3 py-2 text-sm font-medium rounded-t transition-colors ${
                    activeTab === 'fulltext'
                      ? 'bg-white text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  📜 Full Text
                </button>
              )}
            </div>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading article details...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <p className="text-red-600 mb-2">❌ {error}</p>
                <p className="text-sm text-gray-500">This article may not have been processed yet.</p>
              </div>
            </div>
          ) : article ? (
            <>
              {/* Tab: Overview */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  {/* Summary in English */}
                  {article.summary_en && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">📝 Summary (English)</h3>
                      <p className="text-gray-700 leading-relaxed bg-blue-50 p-4 rounded-lg border border-blue-100">
                        {article.summary_en}
                      </p>
                    </div>
                  )}

                  {/* Abstract Original */}
                  {article.abstract && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">📄 Abstract</h3>
                      <p className="text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg">
                        {article.abstract}
                      </p>
                    </div>
                  )}

                  {/* Show message if no abstract or summary */}
                  {!article.abstract && !article.summary_en && (
                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                      <p className="text-amber-800 text-center">
                        ℹ️ No abstract or summary available.<br/>
                        <span className="text-sm">
                          {article.full_text 
                            ? 'You can view the full text in the "Full Text" tab.' 
                            : 'This article may need to be processed.'}
                        </span>
                      </p>
                    </div>
                  )}

                  {/* Quick Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {article.sample_size && (
                      <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                        <div className="text-2xl font-bold text-green-700">{article.sample_size}</div>
                        <div className="text-xs text-green-600">Sample Size</div>
                      </div>
                    )}
                    {article.duration && (
                      <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                        <div className="text-sm font-bold text-purple-700">{article.duration}</div>
                        <div className="text-xs text-purple-600">Duration</div>
                      </div>
                    )}
                    {article.citations !== undefined && article.citations !== null && (
                      <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                        <div className="text-2xl font-bold text-orange-700">{article.citations}</div>
                        <div className="text-xs text-orange-600">Citations</div>
                      </div>
                    )}
                    {article.authors && article.authors.length > 0 && (
                      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <div className="text-2xl font-bold text-blue-700">{article.authors.length}</div>
                        <div className="text-xs text-blue-600">Authors</div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Tab: Full Text */}
              {activeTab === 'fulltext' && article.full_text && (
                <div className="space-y-4">
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg border border-blue-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">📜 Complete Article Text</h3>
                    <p className="text-sm text-gray-600">
                      Full content of the scientific article. You can scroll to read the complete text.
                    </p>
                  </div>
                  
                  <div className="bg-white p-6 rounded-lg border border-gray-200 prose prose-sm max-w-none">
                    <div className="whitespace-pre-wrap text-gray-800 leading-relaxed font-serif">
                      {article.full_text}
                    </div>
                  </div>

                  <div className="flex justify-between items-center bg-gray-50 p-3 rounded text-sm text-gray-600">
                    <span>📏 {article.full_text.length.toLocaleString()} characters</span>
                    <span>📖 ~{Math.ceil(article.full_text.split(/\s+/).length / 200)} min read</span>
                  </div>
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Footer */}
        {!isLoading && !error && article && (
          <div className="px-6 py-4 border-t border-gray-200 flex flex-wrap gap-3">
            {/* Article URL - Primary Button */}
            {article.url && (
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary inline-flex items-center gap-2"
              >
                🔗 View Full Article
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            )}
            
            <button onClick={copyCitation} className="btn-secondary">
              📋 Copy Citation
            </button>
            {article.doi && (
              <>
                <button onClick={copyDoi} className="btn-secondary">
                  📋 Copy DOI
                </button>
                <a
                  href={`https://doi.org/${article.doi}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-secondary"
                >
                  🔗 Open DOI
                </a>
              </>
            )}
            {article.pmid && (
              <a
                href={`https://pubmed.ncbi.nlm.nih.gov/${article.pmid}/`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary"
              >
                🔗 PubMed
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
