import { useState, useEffect } from 'react';
import type { GraphStats, MostConnectedNode } from '../types';
import { getGraphStats } from '../lib/api';

export function GraphStatsView() {
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const data = await getGraphStats();
        setStats(data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Error loading statistics';
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  const getTypeColor = (type: string): string => {
    const colors: Record<string, string> = {
      author: 'bg-blue-100 text-blue-800 border-blue-200',
      institution: 'bg-green-100 text-green-800 border-green-200',
      organism: 'bg-amber-100 text-amber-800 border-amber-200',
      journal: 'bg-purple-100 text-purple-800 border-purple-200',
    };
    return colors[type] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getTypeBadgeColor = (type: string): string => {
    const colors: Record<string, string> = {
      author: 'bg-blue-500',
      institution: 'bg-green-500',
      organism: 'bg-amber-500',
      journal: 'bg-purple-500',
    };
    return colors[type] || 'bg-gray-500';
  };

  const formatEdgeType = (edgeType: string): string => {
    return edgeType
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ↔ ');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading graph statistics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center max-w-md">
          <p className="text-red-600 text-xl mb-2">❌ {error}</p>
          <p className="text-sm text-gray-500">
            Make sure the backend is running and the knowledge graph has been built.
          </p>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <p className="text-gray-500">No statistics available</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">📊 Knowledge Graph Statistics</h1>
          <p className="text-gray-600">Detailed analysis of the scientific collaboration network</p>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
            <div className="text-sm font-medium text-gray-600 mb-1">Total Nodes</div>
            <div className="text-3xl font-bold text-gray-900">{stats.total_nodes.toLocaleString()}</div>
            <div className="text-xs text-gray-500 mt-2">Authors, institutions, organisms, journals</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
            <div className="text-sm font-medium text-gray-600 mb-1">Total Connections</div>
            <div className="text-3xl font-bold text-gray-900">{stats.total_edges.toLocaleString()}</div>
            <div className="text-xs text-gray-500 mt-2">Collaborative relationships</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
            <div className="text-sm font-medium text-gray-600 mb-1">Avg Degree</div>
            <div className="text-3xl font-bold text-gray-900">{stats.avg_degree.toFixed(2)}</div>
            <div className="text-xs text-gray-500 mt-2">Average connections per node</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-amber-500">
            <div className="text-sm font-medium text-gray-600 mb-1">Graph Density</div>
            <div className="text-3xl font-bold text-gray-900">{(stats.density * 100).toFixed(2)}%</div>
            <div className="text-xs text-gray-500 mt-2">Network connectivity ratio</div>
          </div>
        </div>

        {/* Node Types */}
        <div className="bg-white rounded-lg shadow mb-8 p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">🏷️ Node Types Distribution</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(stats.node_types).map(([type, count]) => (
              <div key={type} className="flex items-center gap-3 bg-gray-50 px-4 py-3 rounded-lg">
                <div className={`w-4 h-4 rounded-full ${getTypeBadgeColor(type)}`}></div>
                <div className="flex-1">
                  <div className="text-sm text-gray-600 capitalize">{type}</div>
                  <div className="text-xl font-bold text-gray-900">{count.toLocaleString()}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Degree Distribution */}
        <div className="bg-white rounded-lg shadow mb-8 p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">📈 Degree Distribution</h2>
          <div className="grid grid-cols-5 gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-2">Min</div>
              <div className="text-2xl font-bold text-gray-900">{stats.degree_distribution.min}</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-2">Q1</div>
              <div className="text-2xl font-bold text-blue-600">{stats.degree_distribution.q1}</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-2">Median</div>
              <div className="text-2xl font-bold text-green-600">{stats.degree_distribution.median}</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-2">Q3</div>
              <div className="text-2xl font-bold text-amber-600">{stats.degree_distribution.q3}</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-2">Max</div>
              <div className="text-2xl font-bold text-red-600">{stats.degree_distribution.max}</div>
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-4 text-center">
            50% of nodes have between {stats.degree_distribution.q1} and {stats.degree_distribution.q3} connections
          </p>
        </div>

        {/* Top Connected Nodes */}
        <div className="bg-white rounded-lg shadow mb-8 p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">🌟 Top Connected Nodes</h2>
          <p className="text-sm text-gray-600 mb-4">Most influential entities in the knowledge graph</p>
          
          <div className="space-y-3">
            {stats.top_connected_nodes.map((node: MostConnectedNode, index: number) => (
              <div
                key={node.id}
                className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold">
                  {index + 1}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-900 truncate">{node.name}</span>
                    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium border ${getTypeColor(node.type)}`}>
                      {node.type}
                    </span>
                  </div>
                </div>
                
                <div className="flex-shrink-0 text-right">
                  <div className="text-2xl font-bold text-blue-600">{node.degree}</div>
                  <div className="text-xs text-gray-500">connections</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Network Topology */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">🔗 Network Topology</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Components</span>
                <span className="font-bold text-gray-900">{stats.num_components}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Largest Component</span>
                <span className="font-bold text-gray-900">
                  {stats.largest_component_size} nodes ({((stats.largest_component_size / stats.total_nodes) * 100).toFixed(1)}%)
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Isolated Nodes</span>
                <span className="font-bold text-gray-900">{stats.isolated_nodes}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Avg Clustering</span>
                <span className="font-bold text-gray-900">{(stats.avg_clustering * 100).toFixed(2)}%</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">📏 Degree Range</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Minimum Degree</span>
                <span className="font-bold text-gray-900">{stats.min_degree}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Maximum Degree</span>
                <span className="font-bold text-gray-900">{stats.max_degree}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Range</span>
                <span className="font-bold text-gray-900">{stats.max_degree - stats.min_degree}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Average</span>
                <span className="font-bold text-gray-900">{stats.avg_degree.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Edge Types */}
        <div className="bg-white rounded-lg shadow mb-8 p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">🔀 Connection Types</h2>
          <p className="text-sm text-gray-600 mb-4">Distribution of relationships between different entity types</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(stats.edge_types)
              .sort(([, a], [, b]) => b - a)
              .map(([type, count]) => (
                <div key={type} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-700">{formatEdgeType(type)}</span>
                  <span className="font-bold text-gray-900">{count.toLocaleString()}</span>
                </div>
              ))}
          </div>
          
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 font-medium">Total Connections</span>
              <span className="text-xl font-bold text-gray-900">
                {Object.values(stats.edge_types).reduce((a, b) => a + b, 0).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
