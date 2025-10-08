import { useState, useEffect, useRef } from 'react';
import type { GraphData, NodeDetails } from '../types';
import { getGraph, getNodeDetails, getNodeNeighbors } from '../lib/api';
import { GraphVisualization, GraphVisualizationRef } from './GraphVisualization';

interface GraphViewerProps {
  experimentId: string;
}

export function GraphViewer({ experimentId }: GraphViewerProps) {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [selectedNode, setSelectedNode] = useState<NodeDetails | null>(null);
  const [isNodeModalOpen, setIsNodeModalOpen] = useState(false);
  const [isLoadingNode, setIsLoadingNode] = useState(false);
  const [nodeError, setNodeError] = useState<string | null>(null);

  // Estado para o modal de confirmação de expansão
  const [showExpandModal, setShowExpandModal] = useState(false);
  const [nodeToExpand, setNodeToExpand] = useState<string | null>(null);
  const [isExpanding, setIsExpanding] = useState(false);
  
  // Ref para o componente de visualização
  const graphVisualizationRef = useRef<GraphVisualizationRef>(null);

  useEffect(() => {
    const fetchGraph = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const data = await getGraph(experimentId);
        setGraphData(data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Error loading graph';
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    if (experimentId) {
      fetchGraph();
    }
  }, [experimentId]);

  const handleNodeClick = async (nodeId: string) => {
    // Mostrar modal de confirmação para expandir
    setNodeToExpand(nodeId);
    setShowExpandModal(true);
    
    // Também carregar os detalhes do nó
    setIsNodeModalOpen(true);
    setIsLoadingNode(true);
    setNodeError(null);
    setSelectedNode(null);

    try {
      const nodeDetails = await getNodeDetails(nodeId);
      setSelectedNode(nodeDetails);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error loading node details';
      setNodeError(errorMessage);
    } finally {
      setIsLoadingNode(false);
    }
  };

  const handleExpandNode = async () => {
    if (!nodeToExpand) return;
    setIsExpanding(true);

    try {
      // Buscar vizinhos excluindo nós do experimento atual
      const neighborsData = await getNodeNeighbors(nodeToExpand, 1, experimentId);
    
      // Adicionar novos nós e arestas ao grafo
      if (graphVisualizationRef.current) {
        graphVisualizationRef.current.addNodes(neighborsData.nodes);
        
        graphVisualizationRef.current.addEdges(neighborsData.edges);
        
        // IMPORTANTE: Criar arestas entre o nó expandido e todos os seus vizinhos
        // Isso garante que as conexões sejam visíveis mesmo quando os vizinhos
        // vêm de experimentos diferentes
        const centerNodeId = neighborsData.center_node;
        const additionalEdges = neighborsData.nodes
          .filter(node => node.id !== centerNodeId) // Excluir o próprio nó central
          .map(node => ({
            from: centerNodeId,
            to: node.id,
            value: 1.0, // Peso padrão
            title: 'Connection'
          }));
        
        if (additionalEdges.length > 0) {
          graphVisualizationRef.current.addEdges(additionalEdges);
        }
        
      }

      // Fechar o painel de expansão após sucesso
      setShowExpandModal(false);
      setNodeToExpand(null);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error expanding node';
      alert(`Failed to expand node: ${errorMessage}`);
    } finally {
      setIsExpanding(false);
    }
  };

  const handleCancelExpand = () => {
    setShowExpandModal(false);
    setNodeToExpand(null);
  };

  const handleCloseNodeModal = () => {
    setIsNodeModalOpen(false);
    setSelectedNode(null);
    setNodeError(null);
  };

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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading knowledge graph...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-red-600 mb-2">❌ {error}</p>
          <p className="text-sm text-gray-500">The knowledge graph may not be available for this article.</p>
        </div>
      </div>
    );
  }

  if (!graphData) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-gray-500">No graph data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Graph Visualization */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Grafo - ocupa 2/3 do espaço */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🕸️ Knowledge Graph</h3>
            <p className="text-sm text-gray-600 mb-4">
              💡 Click on any node to see details and expand connections
            </p>
            <GraphVisualization 
              ref={graphVisualizationRef}
              data={graphData} 
              onNodeClick={handleNodeClick} 
            />
          </div>
        </div>

        {/* Painel de Detalhes e Expansão - ocupa 1/3 do espaço */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border border-gray-200 p-4 sticky top-4">
            {!isNodeModalOpen ? (
              <div className="flex items-center justify-center h-full min-h-[400px]">
                <div className="text-center text-gray-500">
                  <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-sm">Click on a node to see details</p>
                </div>
              </div>
            ) : isLoadingNode ? (
              <div className="flex items-center justify-center h-full min-h-[400px]">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600 text-sm">Loading node details...</p>
                </div>
              </div>
            ) : nodeError ? (
              <div className="flex items-center justify-center h-full min-h-[400px]">
                <div className="text-center">
                  <p className="text-red-600 mb-2">❌ {nodeError}</p>
                  <p className="text-sm text-gray-500">Could not load node information.</p>
                </div>
              </div>
            ) : selectedNode ? (
              <div className="space-y-4">
                {/* Header com botão fechar */}
                <div className="flex items-start justify-between pb-3 border-b border-gray-200">
                  <div className="flex-1">
                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium border ${getTypeColor(selectedNode.attributes.type)} mb-2`}>
                      {getTypeLabel(selectedNode.attributes.type)}
                    </span>
                    <h3 className="text-lg font-bold text-gray-900 break-words">{selectedNode.attributes.name}</h3>
                    <div className="flex gap-3 mt-2 text-xs text-gray-600">
                      <span>🔗 {selectedNode.degree}</span>
                      <span>📄 {selectedNode.attributes.experiment_ids.length}</span>
                    </div>
                  </div>
                  <button
                    onClick={handleCloseNodeModal}
                    className="text-gray-400 hover:text-gray-600 text-xl"
                  >
                    ×
                  </button>
                </div>

                {/* Expansão de Nós */}
                {showExpandModal && (
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-lg p-4 shadow-sm">
                    <h4 className="text-sm font-semibold text-blue-900 mb-2 flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Expand Node Connections
                    </h4>
                    <p className="text-xs text-blue-800 mb-3">
                      Add neighboring nodes from other experiments to explore connections.
                    </p>
                    {isExpanding ? (
                      <div className="flex items-center justify-center py-3">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-2"></div>
                        <span className="text-sm text-blue-700 font-medium">Expanding...</span>
                      </div>
                    ) : (
                      <div className="flex gap-2">
                        <button
                          onClick={handleCancelExpand}
                          className="flex-1 px-3 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 border border-gray-300 rounded-lg transition-colors"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={handleExpandNode}
                          className="flex-1 px-3 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors shadow-sm flex items-center justify-center gap-1"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                          </svg>
                          Expand
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* Experiments */}
                {selectedNode.attributes.experiment_ids.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 mb-2">📄 Experiments ({selectedNode.attributes.experiment_ids.length})</h4>
                    <div className="space-y-1 max-h-64 overflow-y-auto">
                      {selectedNode.attributes.experiment_ids.map((expId) => (
                        <a
                          key={expId}
                          href={`https://www.ncbi.nlm.nih.gov/pmc/articles/${expId}/`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block px-2 py-1.5 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded text-xs transition-colors group"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-blue-700 font-mono">{expId}</span>
                            <svg
                              className="w-3 h-3 text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                          </div>
                        </a>
                      ))}
                    </div>
                  </div>
                )}

                {/* Neighbors */}
                {selectedNode.neighbors && selectedNode.neighbors.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 mb-2">🕸️ Connections ({selectedNode.neighbors_count})</h4>
                    <div className="bg-gray-50 rounded p-2 max-h-48 overflow-y-auto">
                      <div className="flex flex-wrap gap-1">
                        {selectedNode.neighbors.slice(0, 30).map((neighbor, idx) => (
                          <span
                            key={idx}
                            className="px-1.5 py-0.5 bg-white border border-gray-300 rounded text-xs text-gray-700"
                          >
                            {neighbor.replace(/^(author|institution|organism|journal):/, '')}
                          </span>
                        ))}
                        {selectedNode.neighbors.length > 30 && (
                          <span className="px-1.5 py-0.5 text-xs text-gray-500 italic">
                            +{selectedNode.neighbors.length - 30} more
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

      {/* Statistics */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Graph Statistics</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div className="text-2xl font-bold text-blue-700">{graphData.stats.total_nodes}</div>
            <div className="text-xs text-blue-600">Total Nodes</div>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <div className="text-2xl font-bold text-green-700">{graphData.stats.total_edges}</div>
            <div className="text-xs text-green-600">Total Connections</div>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
            <div className="text-2xl font-bold text-purple-700">{graphData.stats.avg_degree}</div>
            <div className="text-xs text-purple-600">Avg Degree</div>
          </div>
          
          <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
            <div className="text-2xl font-bold text-amber-700">{graphData.stats.max_degree}</div>
            <div className="text-xs text-amber-600">Max Degree</div>
          </div>
        </div>

        {/* Node Types */}
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Node Types</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {Object.entries(graphData.stats.node_types).map(([type, count]) => (
              <div key={type} className="flex items-center gap-2 bg-gray-50 px-3 py-2 rounded">
                <div className={`w-3 h-3 rounded-full ${
                  type === 'author' ? 'bg-blue-500' :
                  type === 'institution' ? 'bg-green-500' :
                  type === 'organism' ? 'bg-amber-500' :
                  type === 'journal' ? 'bg-purple-500' :
                  'bg-gray-500'
                }`}></div>
                <span className="text-sm text-gray-700 capitalize">{type}:</span>
                <span className="text-sm font-semibold text-gray-900">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Most Connected Node */}
        {graphData.stats.most_connected_node && (
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border border-blue-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">🌟 Most Connected Node</h4>
            <div className="flex items-center gap-3">
              <div className="text-3xl">🔗</div>
              <div className="flex-1">
                <div className="font-semibold text-gray-900">{graphData.stats.most_connected_node.name}</div>
                <div className="text-sm text-gray-600">
                  Type: <span className="capitalize">{graphData.stats.most_connected_node.type}</span>
                  {' • '}
                  Connections: <span className="font-semibold">{graphData.stats.most_connected_node.degree}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">Legend</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-blue-500"></div>
            <span className="text-sm text-gray-700">Authors</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span className="text-sm text-gray-700">Institutions</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-amber-500"></div>
            <span className="text-sm text-gray-700">Organisms</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-purple-500"></div>
            <span className="text-sm text-gray-700">Journals</span>
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-3">
          💡 Tip: You can zoom, drag, and click on nodes to explore the graph. Node size represents the number of connections.
        </p>
      </div>
    </div>
  );
}
