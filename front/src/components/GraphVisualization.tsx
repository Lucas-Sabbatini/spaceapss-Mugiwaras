import { useEffect, useRef } from 'react';
import { Network } from 'vis-network';
import type { GraphData } from '../types';

interface GraphVisualizationProps {
  data: GraphData;
  onNodeClick?: (nodeId: string) => void;
}

export function GraphVisualization({ data, onNodeClick }: GraphVisualizationProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);

  useEffect(() => {
    if (!containerRef.current || !data) return;

    // Define cores para cada grupo
    const groupColors: Record<string, string> = {
      author: '#3b82f6',      // blue
      institution: '#10b981', // green
      organism: '#f59e0b',    // amber
      journal: '#8b5cf6',     // purple
    };

    // Preparar dados para vis-network
    const nodes = data.nodes.map(node => ({
      id: node.id,
      label: undefined, // Remove labels para não poluir
      value: node.value,
      color: {
        background: groupColors[node.group] || '#6b7280',
        border: groupColors[node.group] || '#4b5563',
        highlight: {
          background: groupColors[node.group] || '#6b7280',
          border: '#1f2937',
        },
      },
    }));

    const edges = data.edges.map(edge => ({
      from: edge.from,
      to: edge.to,
      value: edge.value,
      color: {
        color: '#9ca3af',
        highlight: '#3b82f6',
      },
      width: Math.max(1, edge.value / 2),
    }));

    // Opções de configuração da rede
    const options = {
      nodes: {
        shape: 'dot',
        scaling: {
          min: 10,
          max: 30,
        },
        borderWidth: 2,
        shadow: {
          enabled: true,
          color: 'rgba(0,0,0,0.15)',
          size: 5,
          x: 2,
          y: 2,
        },
        font: {
          size: 0, // Oculta completamente os labels
        },
      },
      edges: {
        smooth: {
          enabled: true,
          type: 'continuous',
          roundness: 0.5,
        },
        arrows: {
          to: {
            enabled: false,
          },
        },
        shadow: {
          enabled: true,
          color: 'rgba(0,0,0,0.1)',
          size: 3,
          x: 1,
          y: 1,
        },
      },
      physics: {
        stabilization: {
          enabled: true,
          iterations: 200,
          updateInterval: 25,
        },
        barnesHut: {
          gravitationalConstant: -8000,
          centralGravity: 0.3,
          springLength: 150,
          springConstant: 0.04,
          damping: 0.09,
          avoidOverlap: 0.1,
        },
      },
      interaction: {
        hover: false,
        tooltipDelay: 300,
        navigationButtons: true,
        keyboard: true,
        zoomView: true,
        dragView: true,
      },
      layout: {
        improvedLayout: true,
      },
      autoResize: true,
      height: '100%',
      width: '100%',
    };

    // Criar ou atualizar a rede
    if (networkRef.current) {
      networkRef.current.setData({ nodes, edges });
      networkRef.current.fit({
        animation: {
          duration: 1000,
          easingFunction: 'easeInOutQuad',
        },
      });
    } else {
      networkRef.current = new Network(
        containerRef.current,
        { nodes, edges },
        options
      );

      // Adicionar evento de clique nos nós
      if (onNodeClick) {
        networkRef.current.on('click', (params: any) => {
          if (params.nodes && params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            onNodeClick(nodeId);
          }
        });
      }

      // Ajustar o enquadramento após a estabilização
      networkRef.current.once('stabilizationIterationsDone', () => {
        networkRef.current?.fit({
          animation: {
            duration: 1000,
            easingFunction: 'easeInOutQuad',
          },
        });
      });
    }

    // Cleanup
    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, [data]);

  return (
    <div className="w-full" style={{ height: '600px' }}>
      <div
        ref={containerRef}
        className="w-full h-full border border-gray-300 rounded-lg bg-white"
      />
    </div>
  );
}
