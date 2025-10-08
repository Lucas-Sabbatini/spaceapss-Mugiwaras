"""Service para manipulação do Knowledge Graph."""

import os
from pathlib import Path
from typing import Optional
import networkx as nx

from packages.api.app.graph import KnowledgeGraph


class GraphService:
    """Service para carregar e converter o Knowledge Graph."""
    
    def __init__(self, graph_path: str = None):
        """
        Inicializa o service.
        
        Args:
            graph_path: Caminho para o arquivo .gpickle do grafo.
                       Se None, usa GRAPH_PATH do ambiente ou busca no diretório graphs/
        """
        if graph_path is None:
            # Tentar obter do ambiente
            graph_path = os.getenv("GRAPH_PATH")
            
            # Se não encontrar, buscar arquivo mais recente em graphs/
            if graph_path is None:
                graphs_dir = Path("graphs")
                if graphs_dir.exists():
                    pickle_files = list(graphs_dir.glob("*.gpickle"))
                    if pickle_files:
                        # Pegar o arquivo mais recente
                        graph_path = str(max(pickle_files, key=lambda p: p.stat().st_mtime))
        
        if graph_path is None or not Path(graph_path).exists():
            raise FileNotFoundError(
                "Grafo não encontrado. Configure GRAPH_PATH ou execute build_knowledge_graph.py"
            )
        
        self.graph_path = graph_path
        self.kg = KnowledgeGraph()
        self.kg.load(self.graph_path)
    
    def get_stats(self) -> dict:
        """
        Retorna estatísticas do grafo.
        
        Returns:
            Dicionário com estatísticas
        """
        graph = self.kg.graph
        
        # Contar tipos de nós
        node_types = {}
        for node in graph.nodes():
            node_data = graph.nodes[node]
            node_type = node_data.get('type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        # Calcular métricas de conectividade
        degrees = dict(graph.degree())
        avg_degree = sum(degrees.values()) / len(degrees) if degrees else 0
        max_degree = max(degrees.values()) if degrees else 0
        
        # Nó mais conectado
        most_connected_node = None
        if degrees:
            most_connected_id = max(degrees, key=degrees.get)
            node_data = graph.nodes[most_connected_id]
            most_connected_node = {
                'id': most_connected_id,
                'name': node_data.get('name', most_connected_id),
                'type': node_data.get('type', 'unknown'),
                'degree': degrees[most_connected_id]
            }
        
        return {
            'total_nodes': graph.number_of_nodes(),
            'total_edges': graph.number_of_edges(),
            'node_types': node_types,
            'avg_degree': round(avg_degree, 2),
            'max_degree': max_degree,
            'most_connected_node': most_connected_node
        }
    
    def _node_to_vis(self, node_id: str, graph: nx.Graph) -> dict:
        """
        Converte um nó NetworkX para formato vis.js.
        
        Args:
            node_id: ID do nó
            graph: Grafo NetworkX
            
        Returns:
            Dicionário no formato vis.js
        """
        node_data = graph.nodes[node_id]
        node_type = node_data.get('type', 'unknown')
        name = node_data.get('name', node_id)
        experiment_ids = node_data.get('experiment_ids', [])
        
        # Grau do nó (para tamanho)
        degree = graph.degree(node_id)
        
        # Criar tooltip com informações
        tooltip_parts = [f"<b>{name}</b>", f"Tipo: {node_type}"]
        if experiment_ids:
            exp_count = len(experiment_ids) if isinstance(experiment_ids, list) else 1
            tooltip_parts.append(f"Experimentos: {exp_count}")
            tooltip_parts.append(f"Conexões: {degree}")
        
        return {
            'id': node_id,
            'label': name,
            'group': node_type,
            'title': '<br>'.join(tooltip_parts),
            'value': degree  # Tamanho proporcional ao grau
        }
    
    def _edge_to_vis(self, edge: tuple, graph: nx.Graph) -> dict:
        """
        Converte uma aresta NetworkX para formato vis.js.
        
        Args:
            edge: Tupla (from, to)
            graph: Grafo NetworkX
            
        Returns:
            Dicionário no formato vis.js
        """
        from_node, to_node = edge
        edge_data = graph.get_edge_data(from_node, to_node) or {}
        weight = edge_data.get('weight', 1.0)
        
        return {
            'from': from_node,
            'to': to_node,
            'value': weight,
            'title': f'Peso: {weight}'
        }
    
    def get_graph_data(
        self,
        node_type: Optional[str] = None,
        limit: Optional[int] = None,
        experiment_id: Optional[str] = None,
        min_degree: Optional[int] = None
    ) -> dict:
        """
        Retorna dados do grafo no formato vis.js com filtros aplicados.
        
        Args:
            node_type: Filtrar por tipo de nó
            limit: Limitar número de nós
            experiment_id: Filtrar por experimento
            min_degree: Grau mínimo dos nós
            
        Returns:
            Dicionário com nodes, edges e stats
        """
        graph = self.kg.graph
        
        # Aplicar filtros
        filtered_nodes = []
        
        for node in graph.nodes():
            node_data = graph.nodes[node]
            
            # Filtro por tipo
            if node_type and node_data.get('type') != node_type:
                continue
            
            # Filtro por experiment_id
            if experiment_id:
                exp_ids = node_data.get('experiment_ids', [])
                if isinstance(exp_ids, str):
                    exp_ids = exp_ids.split(',')
                if experiment_id not in exp_ids:
                    continue
            
            # Filtro por grau mínimo
            if min_degree and graph.degree(node) < min_degree:
                continue
            
            filtered_nodes.append(node)
        
        # Aplicar limite
        if limit and len(filtered_nodes) > limit:
            # Ordenar por grau (nós mais conectados primeiro)
            filtered_nodes.sort(key=lambda n: graph.degree(n), reverse=True)
            filtered_nodes = filtered_nodes[:limit]
        
        # Criar subgrafo com nós filtrados
        subgraph = graph.subgraph(filtered_nodes).copy()
        
        # Converter para formato vis.js
        vis_nodes = [self._node_to_vis(node, subgraph) for node in subgraph.nodes()]
        vis_edges = [self._edge_to_vis(edge, subgraph) for edge in subgraph.edges()]
        
        # Estatísticas do subgrafo filtrado
        node_types_count = {}
        for node in subgraph.nodes():
            node_type_val = subgraph.nodes[node].get('type', 'unknown')
            node_types_count[node_type_val] = node_types_count.get(node_type_val, 0) + 1
        
        degrees = dict(subgraph.degree())
        avg_degree = sum(degrees.values()) / len(degrees) if degrees else 0
        max_degree = max(degrees.values()) if degrees else 0
        
        most_connected = None
        if degrees:
            most_connected_id = max(degrees, key=degrees.get)
            node_data = subgraph.nodes[most_connected_id]
            most_connected = {
                'id': most_connected_id,
                'name': node_data.get('name', most_connected_id),
                'type': node_data.get('type', 'unknown'),
                'degree': degrees[most_connected_id]
            }
        
        stats = {
            'total_nodes': len(vis_nodes),
            'total_edges': len(vis_edges),
            'node_types': node_types_count,
            'avg_degree': round(avg_degree, 2),
            'max_degree': max_degree,
            'most_connected_node': most_connected
        }
        
        return {
            'nodes': vis_nodes,
            'edges': vis_edges,
            'stats': stats
        }
    
    def get_node_details(self, node_id: str) -> Optional[dict]:
        """
        Retorna detalhes completos de um nó.
        
        Args:
            node_id: ID do nó
            
        Returns:
            Dicionário com atributos do nó e vizinhos
        """
        graph = self.kg.graph
        
        if node_id not in graph:
            return None
        
        node_data = dict(graph.nodes[node_id])
        
        # Adicionar informações de conectividade
        neighbors = list(graph.neighbors(node_id))
        degree = graph.degree(node_id)
        
        return {
            'id': node_id,
            'attributes': node_data,
            'degree': degree,
            'neighbors_count': len(neighbors),
            'neighbors': neighbors[:20]  # Limitar a 20 vizinhos na resposta
        }
    
    def get_neighbors_subgraph(self, node_id: str, max_depth: int = 1) -> dict:
        """
        Retorna subgrafo de vizinhos no formato vis.js.
        
        Args:
            node_id: ID do nó central
            max_depth: Profundidade da busca (1 = vizinhos diretos)
            
        Returns:
            Dicionário com nodes, edges e stats no formato vis.js
        """
        graph = self.kg.graph
        
        if node_id not in graph:
            raise ValueError(f"Nó '{node_id}' não encontrado no grafo")
        
        # Coletar nós até a profundidade especificada
        nodes_to_include = {node_id}
        current_level = {node_id}
        
        for _ in range(max_depth):
            next_level = set()
            for node in current_level:
                neighbors = set(graph.neighbors(node))
                next_level.update(neighbors)
            nodes_to_include.update(next_level)
            current_level = next_level
        
        # Criar subgrafo
        subgraph = graph.subgraph(nodes_to_include).copy()
        
        # Converter para vis.js
        vis_nodes = [self._node_to_vis(node, subgraph) for node in subgraph.nodes()]
        vis_edges = [self._edge_to_vis(edge, subgraph) for edge in subgraph.edges()]
        
        # Marcar o nó central
        for vis_node in vis_nodes:
            if vis_node['id'] == node_id:
                vis_node['color'] = '#FF0000'  # Destacar em vermelho
                vis_node['font'] = {'size': 20, 'bold': True}
        
        return {
            'nodes': vis_nodes,
            'edges': vis_edges,
            'center_node': node_id,
            'depth': max_depth,
            'stats': {
                'total_nodes': len(vis_nodes),
                'total_edges': len(vis_edges)
            }
        }
