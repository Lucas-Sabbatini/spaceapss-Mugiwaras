"""
Script para construir Knowledge Graph a partir de artigos científicos no MongoDB.

Este script:
1. Conecta ao MongoDB e recupera todos os documentos ArticleMetadata
2. Cria vértices para: Authors, Institutions, Organisms, Journals
3. Cada vértice armazena uma lista de experiment_ids onde aparece
4. Cria arestas conectando todos os elementos do mesmo artigo
5. Salva o grafo em GraphML (Gephi) e Pickle (Python)
"""

import os
import sys
from pathlib import Path
from typing import List, Set, Dict, Any
from datetime import datetime

# Adicionar agents ao sys.path
agents_path = Path(__file__).parent.parent.parent.parent
if str(agents_path) not in sys.path:
    sys.path.insert(0, str(agents_path))

from pymongo import MongoClient
from dotenv import load_dotenv
from packages.api.app.graph import KnowledgeGraph
import networkx as nx

# Carregar variáveis de ambiente
load_dotenv()


class ArticleGraphBuilder:
    """Construtor de grafo de conhecimento a partir de artigos científicos."""
    
    def __init__(self, mongodb_uri: str = None, database_name: str = None, collection_name: str = None):
        """
        Inicializa o construtor.
        
        Args:
            mongodb_uri: URI de conexão MongoDB
            database_name: Nome do database
            collection_name: Nome da collection
        """
        self.mongodb_uri = mongodb_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.database_name = database_name or os.getenv("MONGODB_DATABASE", "spaceapss")
        self.collection_name = collection_name or os.getenv("MONGODB_COLLECTION", "articles")
        
        # Conectar ao MongoDB
        self.client = MongoClient(self.mongodb_uri)
        self.collection = self.client[self.database_name][self.collection_name]
        
        # Criar grafo
        self.kg = KnowledgeGraph()
        
        # Estatísticas
        self.stats = {
            'total_articles': 0,
            'authors': 0,
            'institutions': 0,
            'organisms': 0,
            'journals': 0,
            'edges': 0
        }
        
        print(f"✓ Conectado ao MongoDB: {self.database_name}.{self.collection_name}")
    
    def _normalize_name(self, name: str) -> str:
        """
        Normaliza nomes para evitar duplicatas.
        
        Args:
            name: Nome a ser normalizado
            
        Returns:
            Nome normalizado (lowercase, sem espaços extras)
        """
        if not name:
            return ""
        return " ".join(name.strip().split()).lower()
    
    def _add_or_update_vertex(self, vertex_id: str, vertex_type: str, experiment_id: str, 
                              original_name: str = None) -> None:
        """
        Adiciona vértice ou atualiza lista de experiment_ids se já existir.
        
        Args:
            vertex_id: ID único do vértice (nome normalizado)
            vertex_type: Tipo do vértice (author, institution, organism, journal)
            experiment_id: ID do experimento onde o vértice aparece
            original_name: Nome original antes da normalização
        """
        existing = self.kg.get_entity(vertex_id)
        
        if existing is None:
            # Criar novo vértice
            self.kg.add_entity(
                vertex_id,
                type=vertex_type,
                name=original_name or vertex_id,
                experiment_ids=[experiment_id]
            )
            
            # Atualizar estatísticas
            if vertex_type == 'author':
                self.stats['authors'] += 1
            elif vertex_type == 'institution':
                self.stats['institutions'] += 1
            elif vertex_type == 'organism':
                self.stats['organisms'] += 1
            elif vertex_type == 'journal':
                self.stats['journals'] += 1
        else:
            # Atualizar lista de experiment_ids se ainda não contém
            if experiment_id not in existing['experiment_ids']:
                existing['experiment_ids'].append(experiment_id)
    
    def _process_article(self, article: Dict[str, Any]) -> None:
        """
        Processa um artigo e adiciona vértices e arestas ao grafo.
        
        Args:
            article: Dicionário com dados do artigo
        """
        experiment_id = article.get('experiment_id')
        
        if not experiment_id:
            print(f"⚠ Artigo sem experiment_id, pulando...")
            return
        
        self.stats['total_articles'] += 1
        
        # Coletar todos os vértices deste artigo
        article_vertices = []
        
        # 1. Processar Autores
        authors = article.get('authors', [])
        if authors and isinstance(authors, list):
            for author in authors:
                if author:
                    author_id = f"author:{self._normalize_name(author)}"
                    self._add_or_update_vertex(author_id, 'author', experiment_id, author)
                    article_vertices.append(author_id)
        
        # 2. Processar Instituições
        institutions = article.get('institutions', [])
        if institutions and isinstance(institutions, list):
            for institution in institutions:
                if institution:
                    inst_id = f"institution:{self._normalize_name(institution)}"
                    self._add_or_update_vertex(inst_id, 'institution', experiment_id, institution)
                    article_vertices.append(inst_id)
        
        # 3. Processar Organismos
        organisms = article.get('organisms', [])
        if organisms and isinstance(organisms, list):
            for organism in organisms:
                if organism:
                    org_id = f"organism:{self._normalize_name(organism)}"
                    self._add_or_update_vertex(org_id, 'organism', experiment_id, organism)
                    article_vertices.append(org_id)
        
        # 5. Processar Journal
        journal = article.get('journal')
        if journal:
            journal_id = f"journal:{self._normalize_name(journal)}"
            self._add_or_update_vertex(journal_id, 'journal', experiment_id, journal)
            article_vertices.append(journal_id)
        
        # 6. Criar arestas entre todos os vértices deste artigo
        # Conectar cada par de vértices (grafo completo dos elementos do artigo)
        for i, v1 in enumerate(article_vertices):
            for v2 in article_vertices[i+1:]:
                # Adicionar aresta (incrementa peso se já existir)
                self.kg.add_relationship(v1, v2, weight=1.0)
                self.stats['edges'] += 1
        
        # Log de progresso
        if self.stats['total_articles'] % 10 == 0:
            print(f"  Processados {self.stats['total_articles']} artigos...")
    
    def build_graph(self) -> KnowledgeGraph:
        """
        Constrói o grafo completo a partir de todos os artigos no MongoDB.
        
        Returns:
            KnowledgeGraph construído
        """
        
        # Contar total de documentos
        total_docs = self.collection.count_documents({})
        print(f"📊 Total de documentos no MongoDB: {total_docs}\n")
        
        if total_docs == 0:
            print("⚠ Nenhum documento encontrado!")
            return self.kg
        
        # Processar todos os documentos
        print("🔄 Processando documentos...\n")
        
        for article in self.collection.find():
            try:
                self._process_article(article)
            except Exception as e:
                print(f"❌ Erro ao processar artigo {article.get('experiment_id', 'unknown')}: {e}")
                continue
        
        print(f"\n✓ Processamento concluído!\n")
        
        return self.kg
    
    def print_statistics(self) -> None:
        """Imprime estatísticas do grafo construído."""
        print("\n" + "="*80)
        print(" ESTATÍSTICAS DO GRAFO")
        print("="*80 + "\n")
        
        print(f"📚 Artigos processados: {self.stats['total_articles']}")
        print(f"\n📊 Vértices criados:")
        print(f"  👤 Autores:       {self.stats['authors']}")
        print(f"  🏛️  Instituições:  {self.stats['institutions']}")
        print(f"  🧬 Organismos:    {self.stats['organisms']}")
        print(f"  📖 Journals:      {self.stats['journals']}")
        print(f"\n🔗 Total de vértices: {self.kg.graph.number_of_nodes()}")
        print(f"🔗 Total de arestas:  {self.kg.graph.number_of_edges()}")
        
        # Estatísticas adicionais
        if self.kg.graph.number_of_nodes() > 0:
            degrees = dict(self.kg.graph.degree())
            avg_degree = sum(degrees.values()) / len(degrees)
            max_degree = max(degrees.values())
            max_degree_node = max(degrees, key=degrees.get)
            
            print(f"\n📈 Análise de conectividade:")
            print(f"  Grau médio:      {avg_degree:.2f}")
            print(f"  Grau máximo:     {max_degree}")
            
            # Mostrar informação do nó mais conectado
            max_node_data = self.kg.get_entity(max_degree_node)
            print(f"  Nó mais conectado: {max_node_data.get('name', max_degree_node)}")
            print(f"                     (tipo: {max_node_data.get('type')}, conexões: {max_degree})")
        
        print("\n" + "="*80 + "\n")
    
    def save_graph(self, output_dir: str = ".", base_name: str = None) -> None:
        """
        Salva o grafo em múltiplos formatos.
        
        Args:
            output_dir: Diretório de saída
            base_name: Nome base dos arquivos (default: knowledge_graph_<timestamp>)
        """
        # Criar nome base com timestamp
        if base_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"knowledge_graph_{timestamp}"
        
        # Criar diretório se não existir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        print("💾 Salvando grafo...\n")
        
        # 1. Salvar em GraphML (para Gephi)
        graphml_path = Path(output_dir) / f"{base_name}.graphml"
        self.kg.save_graphml(str(graphml_path))
        print(f"  ✓ GraphML (Gephi): {graphml_path}")
        
        # 2. Salvar em Pickle (para Python)
        pickle_path = Path(output_dir) / f"{base_name}.gpickle"
        self.kg.save(str(pickle_path))
        print(f"  ✓ Pickle (Python): {pickle_path}")
        
        # 3. Salvar em JSON (formato node-link)
        json_path = Path(output_dir) / f"{base_name}.json"
        import json
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.kg.toJson(), f, indent=2, ensure_ascii=False)
        print(f"  ✓ JSON (node-link): {json_path}")

        
        # 4. Salvar estatísticas em texto
        stats_path = Path(output_dir) / f"{base_name}_stats.txt"
        with open(stats_path, 'w', encoding='utf-8') as f:
            f.write("KNOWLEDGE GRAPH STATISTICS\n")
            f.write("="*80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Articles processed: {self.stats['total_articles']}\n")
            f.write(f"\nVertices:\n")
            f.write(f"  Authors:       {self.stats['authors']}\n")
            f.write(f"  Institutions:  {self.stats['institutions']}\n")
            f.write(f"  Organisms:     {self.stats['organisms']}\n")
            f.write(f"  Journals:      {self.stats['journals']}\n")
            f.write(f"\nTotal vertices:  {self.kg.graph.number_of_nodes()}\n")
            f.write(f"Total edges:     {self.kg.graph.number_of_edges()}\n")
        print(f"  ✓ Statistics: {stats_path}")
        
        print(f"\n✅ Grafo salvo com sucesso!\n")
        print(f"📝 Nota: No GraphML, experiment_ids foi convertido para string (separado por vírgulas)")
        print(f"   Para preservar as listas originais, use os arquivos Pickle ou JSON.\n")
    
    def close(self):
        """Fecha conexão com MongoDB."""
        self.client.close()
        print("✓ Conexão MongoDB fechada")


def main():
    """Função principal."""
    print(" KNOWLEDGE GRAPH BUILDER - Scientific Articles")
    
    try:
        # Criar construtor
        builder = ArticleGraphBuilder()
        
        # Construir grafo
        kg = builder.build_graph()
        
        # Mostrar estatísticas
        builder.print_statistics()
        
        # Salvar grafo
        output_dir = os.getenv("GRAPH_OUTPUT_DIR", "./graphs")
        builder.save_graph(output_dir=output_dir)
        
        # Fechar conexão
        builder.close()
        
        print(" PROCESSO CONCLUÍDO COM SUCESSO!")
        
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
