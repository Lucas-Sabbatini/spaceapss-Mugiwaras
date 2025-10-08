import networkx as nx
import pickle

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