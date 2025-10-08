import networkx as nx
import pickle
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Dict, Tuple

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.Graph()

    def add_entity(self, entity_id: str, **attributes):
        if entity_id not in self.graph:
            self.graph.add_node(entity_id, **attributes)
        
    def get_entity(self, entity_id: str):
        return self.graph.nodes[entity_id] if entity_id in self.graph else None
    
    def add_relationship(self, entity1_id: str, entity2_id: str,weight: float = 1.0):
        if entity1_id not in self.graph or entity2_id not in self.graph:
            return
        
        if not self.graph.has_edge(entity1_id, entity2_id):
            self.graph.add_edge(entity1_id, entity2_id, weight=weight)
            return
        
        self.graph[entity1_id][entity2_id]['weight'] += 1

    def get_relationship(self, entity1_id: str, entity2_id: str):
        return self.graph.get_edge_data(entity1_id, entity2_id)

    def load(self, path = "knowledge_graph.gpickle"):
        """Carrega o grafo de um arquivo Pickle."""
        with open(path, 'rb') as f:
            self.graph = pickle.load(f)
    
    def save_graphml(self, path = "knowledge_graph.graphml"):
        """
        Salva o grafo em formato GraphML (compatível com Gephi).
        
        GraphML não suporta listas como valores de atributos, então
        converte automaticamente campos do tipo list para string CSV.
        
        Args:
            path: Caminho do arquivo GraphML a ser criado
        """
        # Criar cópia do grafo para converter listas em strings
        graphml_graph = self.graph.copy()
        
        # Processar nós: converter listas para strings CSV
        for node in graphml_graph.nodes():
            node_data = graphml_graph.nodes[node]
            for key, value in list(node_data.items()):
                if isinstance(value, list):
                    # Converter lista para string separada por vírgulas
                    node_data[key] = ','.join(str(v) for v in value)
        
        # Processar arestas: converter listas para strings CSV
        for edge in graphml_graph.edges():
            edge_data = graphml_graph.edges[edge]
            for key, value in list(edge_data.items()):
                if isinstance(value, list):
                    edge_data[key] = ','.join(str(v) for v in value)
        
        # Salvar em GraphML
        nx.write_graphml(graphml_graph, path)
    
    def save(self, path = "knowledge_graph.gpickle"):
        """Salva o grafo em formato Pickle."""
        with open(path, 'wb') as f:
            pickle.dump(self.graph, f)
    
    def toJson(self):
        return nx.node_link_data(self.graph)
    
    def get_node_colors(self) -> Dict[str, str]:
        """
        Retorna o mapeamento de cores por tipo de nó.
        Usa as mesmas cores do front-end para consistência visual.
        
        Returns:
            Dicionário com tipo -> cor HEX
        """
        return {
            'author': '#3B82F6',      # blue-500
            'institution': '#10B981',  # green-500
            'organism': '#F59E0B',     # amber-500
            'journal': '#A855F7',      # purple-500
            'default': '#6B7280'       # gray-500
        }
    
    def _get_node_color(self, node_id: str) -> str:
        """
        Obtém a cor de um nó baseado no seu tipo.
        
        Args:
            node_id: ID do nó
            
        Returns:
            Cor HEX para o nó
        """
        node_data = self.graph.nodes.get(node_id, {})
        node_type = node_data.get('type', 'default')
        colors = self.get_node_colors()
        return colors.get(node_type, colors['default'])
    
    def _get_node_size(self, node_id: str, base_size: int = 300, scale: float = 100.0) -> float:
        """
        Calcula o tamanho do nó baseado no seu grau (número de conexões).
        
        Args:
            node_id: ID do nó
            base_size: Tamanho base para nós
            scale: Fator de escala para o grau
            
        Returns:
            Tamanho do nó
        """
        degree = self.graph.degree[node_id]
        return base_size + (degree * scale)
    
    def generate_graph_image(
        self,
        output_path: str = "knowledge_graph.png",
        figsize: Tuple[int, int] = (24, 18),
        dpi: int = 300,
        layout: str = "spring",
        iterations: int = 100,
        k: float = 0.5,
        node_base_size: int = 300,
        node_size_scale: float = 100.0,
        edge_width: float = 0.3,
        edge_alpha: float = 0.4,
        font_size: int = 8,
        show_labels: bool = True,
        show_legend: bool = True,
        title: str = "Knowledge Graph - Scientific Articles",
        background_color: str = "#FFFFFF"
    ) -> str:
        """
        Gera uma imagem visual detalhada do grafo de conhecimento.
        
        Args:
            output_path: Caminho do arquivo de saída
            figsize: Tamanho da figura (largura, altura) em polegadas
            dpi: Resolução da imagem
            layout: Algoritmo de layout ("spring", "kamada_kawai", "circular", "random")
            iterations: Número de iterações para layout spring
            k: Distância ótima entre nós (spring layout)
            node_base_size: Tamanho base dos nós
            node_size_scale: Escala adicional baseada no grau do nó
            edge_width: Largura das arestas
            edge_alpha: Transparência das arestas (0-1)
            font_size: Tamanho da fonte dos labels
            show_labels: Se deve mostrar labels dos nós
            show_legend: Se deve mostrar legenda
            title: Título do grafo
            background_color: Cor de fundo
            
        Returns:
            Caminho do arquivo gerado
        """
        if self.graph.number_of_nodes() == 0:
            raise ValueError("O grafo está vazio. Não é possível gerar imagem.")
        
        print(f"🎨 Gerando visualização do grafo...")
        print(f"   Nós: {self.graph.number_of_nodes()}, Arestas: {self.graph.number_of_edges()}")
        
        # Criar figura
        fig, ax = plt.subplots(figsize=figsize, facecolor=background_color)
        ax.set_facecolor(background_color)
        
        # Calcular layout
        print(f"   Layout: {layout}")
        if layout == "spring":
            pos = nx.spring_layout(
                self.graph,
                k=k,
                iterations=iterations,
                seed=42  # Para reprodutibilidade
            )
        elif layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(self.graph)
        elif layout == "circular":
            pos = nx.circular_layout(self.graph)
        elif layout == "random":
            pos = nx.random_layout(self.graph, seed=42)
        else:
            raise ValueError(f"Layout '{layout}' não suportado. Use: spring, kamada_kawai, circular, random")
        
        # Preparar cores e tamanhos dos nós
        node_colors = [self._get_node_color(node) for node in self.graph.nodes()]
        node_sizes = [self._get_node_size(node, node_base_size, node_size_scale) for node in self.graph.nodes()]
        
        # Desenhar arestas
        nx.draw_networkx_edges(
            self.graph,
            pos,
            width=edge_width,
            alpha=edge_alpha,
            edge_color='#9CA3AF',  # gray-400
            ax=ax
        )
        
        # Desenhar nós
        nx.draw_networkx_nodes(
            self.graph,
            pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.9,
            linewidths=1.5,
            edgecolors='#FFFFFF',
            ax=ax
        )
        
        # Desenhar labels (se habilitado)
        if show_labels:
            # Criar labels simplificados (remover prefixo de tipo)
            labels = {}
            for node in self.graph.nodes():
                node_data = self.graph.nodes[node]
                name = node_data.get('name', node)
                # Limitar tamanho do label
                if len(name) > 30:
                    name = name[:27] + "..."
                labels[node] = name
            
            nx.draw_networkx_labels(
                self.graph,
                pos,
                labels,
                font_size=font_size,
                font_weight='bold',
                font_color='#1F2937',  # gray-800
                ax=ax
            )
        
        # Adicionar legenda
        if show_legend:
            colors_map = self.get_node_colors()
            legend_elements = [
                mpatches.Patch(color=colors_map['author'], label=f'Authors ({sum(1 for n in self.graph.nodes() if self.graph.nodes[n].get("type") == "author")})'),
                mpatches.Patch(color=colors_map['institution'], label=f'Institutions ({sum(1 for n in self.graph.nodes() if self.graph.nodes[n].get("type") == "institution")})'),
                mpatches.Patch(color=colors_map['organism'], label=f'Organisms ({sum(1 for n in self.graph.nodes() if self.graph.nodes[n].get("type") == "organism")})'),
                mpatches.Patch(color=colors_map['journal'], label=f'Journals ({sum(1 for n in self.graph.nodes() if self.graph.nodes[n].get("type") == "journal")})'),
            ]
            ax.legend(
                handles=legend_elements,
                loc='upper left',
                fontsize=12,
                framealpha=0.95,
                edgecolor='#E5E7EB',
                facecolor='#F9FAFB'
            )
        
        # Adicionar título
        if title:
            plt.title(
                title,
                fontsize=20,
                fontweight='bold',
                color='#111827',  # gray-900
                pad=20
            )
        
        # Adicionar estatísticas como subtítulo
        degrees = dict(self.graph.degree())
        avg_degree = sum(degrees.values()) / len(degrees) if degrees else 0
        max_degree = max(degrees.values()) if degrees else 0
        
        stats_text = f"Nodes: {self.graph.number_of_nodes()} | Edges: {self.graph.number_of_edges()} | Avg Degree: {avg_degree:.1f} | Max Degree: {max_degree}"
        plt.text(
            0.5, 0.98,
            stats_text,
            transform=fig.transFigure,
            ha='center',
            va='top',
            fontsize=12,
            color='#6B7280',  # gray-500
            style='italic'
        )
        
        # Remover eixos
        ax.axis('off')
        
        # Ajustar layout
        plt.tight_layout()
        
        # Salvar imagem
        print(f"   Salvando em: {output_path}")
        plt.savefig(
            output_path,
            dpi=dpi,
            bbox_inches='tight',
            facecolor=background_color,
            edgecolor='none'
        )
        plt.close()
        
        print(f"✅ Imagem gerada com sucesso: {output_path}")
        return output_path