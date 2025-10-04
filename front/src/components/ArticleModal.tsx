import { useState } from 'react';
import type { Article } from '../types';

interface ArticleModalProps {
  article: Article | null;
  isOpen: boolean;
  onClose: () => void;
}

export function ArticleModal({ article, isOpen, onClose }: ArticleModalProps) {
  const [expandedSections, setExpandedSections] = useState<Set<number>>(new Set());

  if (!isOpen || !article) return null;

  const toggleSection = (index: number) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedSections(newExpanded);
  };

  const copyCitation = () => {
    const citation = `${article.authors.join(', ')} (${article.year}). ${article.title}. ${article.doi ? `DOI: ${article.doi}` : ''}`;
    navigator.clipboard.writeText(citation);
    alert('Citação copiada!');
  };

  const copyDoi = () => {
    if (article.doi) {
      navigator.clipboard.writeText(article.doi);
      alert('DOI copiado!');
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-start justify-between sticky top-0 bg-white rounded-t-lg">
          <div className="flex-1 pr-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">{article.title}</h2>
            <p className="text-sm text-gray-600">
              {article.authors.join(', ')} • {article.year}
            </p>
            <div className="flex gap-2 mt-2">
              {article.doi && (
                <a
                  href={`https://doi.org/${article.doi}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:underline"
                >
                  DOI: {article.doi}
                </a>
              )}
              {article.url && (
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:underline"
                >
                  🔗 URL
                </a>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-light"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {/* Abstract */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Resumo</h3>
            <p className="text-gray-700 leading-relaxed">{article.abstract}</p>
          </div>

          {/* Sections */}
          {article.sections && article.sections.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Seções</h3>
              <div className="space-y-2">
                {article.sections.map((section, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg">
                    <button
                      onClick={() => toggleSection(index)}
                      className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                    >
                      <span className="font-medium text-gray-900">{section.heading}</span>
                      <span className="text-gray-500">
                        {expandedSections.has(index) ? '−' : '+'}
                      </span>
                    </button>
                    {expandedSections.has(index) && (
                      <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
                        <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                          {section.content}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* References */}
          {article.references && article.references.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Referências</h3>
              <ul className="space-y-2">
                {article.references.map((ref, index) => (
                  <li key={index} className="text-sm text-gray-700 pl-4">
                    <span className="text-gray-500">[{index + 1}]</span> {ref}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Metadata */}
          {article.metadata && Object.keys(article.metadata).length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Metadados</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                {article.metadata.keywords && (
                  <div className="mb-2">
                    <span className="font-medium text-gray-700">Palavras-chave: </span>
                    <span className="text-gray-600">
                      {Array.isArray(article.metadata.keywords)
                        ? article.metadata.keywords.join(', ')
                        : article.metadata.keywords}
                    </span>
                  </div>
                )}
                {article.metadata.journal && (
                  <div className="mb-2">
                    <span className="font-medium text-gray-700">Jornal: </span>
                    <span className="text-gray-600">{article.metadata.journal}</span>
                  </div>
                )}
                {article.metadata.impact_factor && (
                  <div>
                    <span className="font-medium text-gray-700">Fator de Impacto: </span>
                    <span className="text-gray-600">{article.metadata.impact_factor}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex gap-3">
          <button onClick={copyCitation} className="btn-secondary">
            📋 Copiar Citação
          </button>
          {article.doi && (
            <button onClick={copyDoi} className="btn-secondary">
              📋 Copiar DOI
            </button>
          )}
          {article.url && (
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary"
            >
              🔗 Abrir URL
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
