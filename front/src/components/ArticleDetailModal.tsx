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
  const [activeTab, setActiveTab] = useState<'overview' | 'details' | 'findings' | 'metadata'>('overview');

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
              <button
                onClick={() => setActiveTab('details')}
                className={`px-3 py-2 text-sm font-medium rounded-t transition-colors ${
                  activeTab === 'details'
                    ? 'bg-white text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                🔬 Experimental Details
              </button>
              <button
                onClick={() => setActiveTab('findings')}
                className={`px-3 py-2 text-sm font-medium rounded-t transition-colors ${
                  activeTab === 'findings'
                    ? 'bg-white text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                💡 Findings
              </button>
              <button
                onClick={() => setActiveTab('metadata')}
                className={`px-3 py-2 text-sm font-medium rounded-t transition-colors ${
                  activeTab === 'metadata'
                    ? 'bg-white text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📊 Metadata
              </button>
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
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">📄 Abstract (Original)</h3>
                      <p className="text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg">
                        {article.abstract}
                      </p>
                    </div>
                  )}

                  {/* Quick Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {article.sample_size && (
                      <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                        <div className="text-2xl font-bold text-green-700">{article.sample_size}</div>
                        <div className="text-xs text-green-600">Tamanho da Amostra</div>
                      </div>
                    )}
                    {article.duration && (
                      <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                        <div className="text-sm font-bold text-purple-700">{article.duration}</div>
                        <div className="text-xs text-purple-600">Duração</div>
                      </div>
                    )}
                    {article.citations !== undefined && (
                      <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                        <div className="text-2xl font-bold text-orange-700">{article.citations}</div>
                        <div className="text-xs text-orange-600">Citations</div>
                      </div>
                    )}
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                      <div className="text-2xl font-bold text-blue-700">{article.authors.length}</div>
                      <div className="text-xs text-blue-600">Authors</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab: Experimental Details */}
              {activeTab === 'details' && (
                <div className="space-y-6">
                  {article.objectives.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">🎯 Objectives</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {article.objectives.map((obj, i) => (
                          <li key={i} className="text-gray-700">{obj}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {article.hypotheses.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">🔬 Hypotheses</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {article.hypotheses.map((hyp, i) => (
                          <li key={i} className="text-gray-700">{hyp}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {article.organisms.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">🧬 Organisms Studied</h3>
                      <div className="flex flex-wrap gap-2">
                        {article.organisms.map((org, i) => (
                          <span key={i} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                            {org}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {article.conditions.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">⚗️ Experimental Conditions</h3>
                      <div className="flex flex-wrap gap-2">
                        {article.conditions.map((cond, i) => (
                          <span key={i} className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                            {cond}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {article.methods.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">🔧 Methods</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {article.methods.map((method, i) => (
                          <li key={i} className="text-gray-700">{method}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {article.parameters_measured.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">📊 Parameters Measured</h3>
                      <div className="flex flex-wrap gap-2">
                        {article.parameters_measured.map((param, i) => (
                          <span key={i} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                            {param}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {article.conditions_control.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">🧪 Control Groups</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {article.conditions_control.map((ctrl, i) => (
                          <li key={i} className="text-gray-700">{ctrl}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Tab: Findings */}
              {activeTab === 'findings' && (
                <div className="space-y-6">
                  {article.results_summary && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">📈 Results Summary</h3>
                      <p className="text-gray-700 leading-relaxed bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                        {article.results_summary}
                      </p>
                    </div>
                  )}

                  {article.significant_findings.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">💡 Significant Findings</h3>
                      <ul className="space-y-2">
                        {article.significant_findings.map((finding, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-green-600 font-bold mt-1">✓</span>
                            <span className="text-gray-700">{finding}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {article.implications.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">🎯 Implications</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {article.implications.map((impl, i) => (
                          <li key={i} className="text-gray-700">{impl}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {article.limitations.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">⚠️ Limitations</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {article.limitations.map((lim, i) => (
                          <li key={i} className="text-gray-600">{lim}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {article.future_directions.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">🚀 Future Directions</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {article.future_directions.map((dir, i) => (
                          <li key={i} className="text-gray-700">{dir}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Tab: Metadata */}
              {activeTab === 'metadata' && (
                <div className="space-y-6">
                  {article.institutions.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">🏛️ Institutions</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {article.institutions.map((inst, i) => (
                          <li key={i} className="text-gray-700 text-sm">{inst}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {article.funding.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">💰 Funding</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {article.funding.map((fund, i) => (
                          <li key={i} className="text-gray-700 text-sm">{fund}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {article.mesh_terms.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">🏷️ MeSH Terms</h3>
                      <div className="flex flex-wrap gap-2">
                        {article.mesh_terms.map((term, i) => (
                          <span key={i} className="bg-indigo-100 text-indigo-800 px-2 py-1 rounded text-xs">
                            {term}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {article.related_projects.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">🔗 Related Projects</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {article.related_projects.map((proj, i) => (
                          <li key={i} className="text-gray-700">{proj}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {article.authors.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">👥 All Authors</h3>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-700">{article.authors.join(', ')}</p>
                      </div>
                    </div>
                  )}

                  {(article.created_at || article.updated_at) && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">📅 Dates</h3>
                      <div className="bg-gray-50 p-4 rounded-lg space-y-1 text-sm">
                        {article.created_at && (
                          <p><span className="font-medium">Created:</span> {new Date(article.created_at).toLocaleString('en-US')}</p>
                        )}
                        {article.updated_at && (
                          <p><span className="font-medium">Updated:</span> {new Date(article.updated_at).toLocaleString('en-US')}</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Footer */}
        {!isLoading && !error && article && (
          <div className="px-6 py-4 border-t border-gray-200 flex gap-3">
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
