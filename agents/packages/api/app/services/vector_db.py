"""Gerenciador de banco de dados vetorial usando ChromaDB."""

import chromadb
from chromadb.types import Collection
import uuid
import os
from pathlib import Path


def dict_to_string(retrieval: dict) -> str:
    """Converte dicionário para string extraindo a fonte."""
    return retrieval["source"]


def string_to_dict(source_string: str) -> dict:
    """Converte string para dicionário com metadados."""
    return {"source": source_string}


class VectorDBManager:
    """
    Uma classe para gerenciar operações com o ChromaDB.

    Atributos:
        collection (Collection): O objeto de coleção do ChromaDB.
    """

    def __init__(self, db_path: str | None = None):
        """
        Inicializa o gerenciador do banco de dados vetorial.
        
        Args:
            db_path: Caminho para o diretório do ChromaDB. Se None, usa o diretório padrão.
        """
        if db_path is None:
            # Define o caminho padrão como agents/chroma_db
            current_file = Path(__file__).resolve()
            # Navega até o diretório agents (4 níveis acima: services -> app -> api -> packages -> agents)
            agents_dir = current_file.parent.parent.parent.parent.parent
            db_path = str(agents_dir / "chroma_db")
        
        # Garante que o diretório existe
        os.makedirs(db_path, exist_ok=True)
        
        chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection: Collection = chroma_client.get_or_create_collection(
            name="nasa_space_collection"
        )

    def add_document(self, document: str, text: str) -> None:
        """
        Adiciona ou atualiza um documento na coleção.
        
        Args:
            document: Conteúdo do documento
            text: Texto de metadados (fonte)
        """
        metadata = string_to_dict(text)
        self.collection.upsert(
            documents=[document],
            metadatas=[metadata],
            ids=str(uuid.uuid4())
        )
        print(f"Documento adicionado/atualizado.")

    def add_document_id(self, document: str, text: str, doc_id: str) -> None:
        """
        Adiciona ou atualiza um documento na coleção com ID específico.
        Args:
            document: Conteúdo do documento
            text: Texto de metadados (fonte)    
            doc_id: ID do documento
        """
        metadata = string_to_dict(text)
        self.collection.upsert(
            documents=[document],
            metadatas=[metadata],
            ids=[doc_id]
        )
        print(f"Documento adicionado/atualizado.")


    def query(self, query_text: str, n_results: int = 2) -> list[str]:
        """
        Realiza uma busca na coleção.
        
        Args:
            query_text: Texto da pergunta/query
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de strings relacionadas à pergunta
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        # Extrair metadados e converter para lista de strings
        metadatas_list = results.get("metadatas", [[]])[0]
        result_formatted = list(map(dict_to_string, metadatas_list))
        
        return result_formatted
    
    def query_with_metadata(self, query_text: str, n_results: int = 2) -> list[dict]:
        """
        Realiza uma busca na coleção retornando metadados estruturados.
        
        Args:
            query_text: Texto da pergunta/query
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de dicionários com dados estruturados dos documentos
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Processar resultados
        formatted_results = []
        
        if results and results.get('ids'):
            ids = results['ids'][0]
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            for i in range(len(ids)):
                # Parse do metadata string para extrair informações
                metadata_str = metadatas[i].get('source', '')
                
                # Tentar parsear as informações do metadata
                parsed_data = self._parse_metadata_string(metadata_str)
                
                # Calcular score garantindo que esteja entre 0 e 1
                distance = distances[i] if i < len(distances) else 1.0
                # Normalizar: quanto menor a distância, maior o score
                # Garantir que score >= 0 usando max(0, ...)
                score = max(0.0, min(1.0, 1.0 - distance))
                
                formatted_results.append({
                    'id': ids[i],
                    'document': documents[i] if i < len(documents) else '',
                    'title': parsed_data.get('title', 'Unknown Title'),
                    'url': parsed_data.get('url', ''),
                    'content': parsed_data.get('content', ''),
                    'distance': distance,
                    'score': score
                })
        
        return formatted_results
    
    def _parse_metadata_string(self, metadata_str: str) -> dict:
        """
        Parse metadata string para extrair título, URL e conteúdo.
        
        Formato esperado: 'title': '...', 'url': '...', 'content': '...'
        """
        import re
        
        result = {
            'title': '',
            'url': '',
            'content': ''
        }
        
        # Extrair título
        title_match = re.search(r"'title':\s*'([^']*)'", metadata_str)
        if title_match:
            result['title'] = title_match.group(1).replace("\\'", "'")
        
        # Extrair URL
        url_match = re.search(r"'url':\s*'([^']*)'", metadata_str)
        if url_match:
            result['url'] = url_match.group(1)
        
        # Extrair content
        content_match = re.search(r"'content':\s*'(.*)'$", metadata_str)
        if content_match:
            result['content'] = content_match.group(1).replace("\\'", "'").replace('\\"', '"')
        
        return result


if __name__ == "__main__":
    """Teste da classe VectorDBManager com dados do artigo Bion-M 1."""
    
    print("=" * 70)
    print("TESTE DO VectorDBManager - Artigo Bion-M 1")
    print("=" * 70)
    
    # Inicializar o VectorDBManager
    print("\n1. Inicializando VectorDBManager...")
    db_manager = VectorDBManager()
    print("✅ VectorDBManager inicializado com sucesso!")
    
    # Dados do artigo sobre Bion-M 1 mission
    print("\n2. Adicionando documento sobre Bion-M 1 mission...")
    
    document_content = """After a 16-year hiatus, Russia resumed in 2013 its program of biomedical 
    research in space, with the successful 30-day flight of the Bion-M 1 biosatellite 
    (April 19–May 19, 2013), a specially designed automated spacecraft dedicated to 
    life-science experiments. The principal animal species for physiological studies 
    in this mission was the mouse (Mus musculus). The challenging task of supporting 
    mice in space for this unmanned, automated, 30-day-long mission, was made even 
    more so by the requirement to house the males in groups. The scientific program 
    was aimed at obtaining data on mechanisms of adaptation of muscle, bone, 
    cardiovascular, sensorimotor and nervous systems to prolonged exposure in 
    microgravity and during post-flight recovery."""
    
    db_manager.add_document(
        document=document_content,
        text=document_content
    )
    
    print("\n3. Adicionando documento sobre efeitos da microgravidade em células...")
    
    document_content_2 = """Microgravity conditions in space significantly affect stem 
    cell differentiation processes. Researchers found that mesenchymal stem cells 
    exhibit altered gene expression patterns when exposed to microgravity, particularly 
    in genes related to osteogenic and adipogenic differentiation. These findings have 
    important implications for long-duration space missions and potential therapeutic 
    applications on Earth. Space environment affects microorganisms by increasing their 
    virulence; major shifts in immune status in space are well documented."""
    
    db_manager.add_document(
        document=document_content_2,
        text=document_content_2
    )
    
    # Testar queries
    print("\n4. Testando queries...")
    
    # Query 1: Sobre a missão Bion-M 1
    print("\n   Query 1: 'What was the Bion-M 1 mission?'")
    results = db_manager.query(
        query_text="What was the Bion-M 1 mission?",
        n_results=2
    )
    print(f"   Resultados encontrados: {len(results)}")
    for idx, result in enumerate(results, 1):
        print(f"   [{idx}] {result}")
    
    # Query 2: Sobre microgravidade
    print("\n   Query 2: 'How does microgravity affect cells?'")
    results = db_manager.query(
        query_text="How does microgravity affect cells?",
        n_results=2
    )
    print(f"   Resultados encontrados: {len(results)}")
    for idx, result in enumerate(results, 1):
        print(f"   [{idx}] {result}")
    
    # Query 3: Em português
    print("\n   Query 3: 'Quais os efeitos do espaço em animais?'")
    results = db_manager.query(
        query_text="Quais os efeitos do espaço em animais?",
        n_results=2
    )
    print(f"   Resultados encontrados: {len(results)}")
    for idx, result in enumerate(results, 1):
        print(f"   [{idx}] {result}")
    
    print("\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    print("\nO banco vetorial ChromaDB foi populado e testado.")
    print("Agora você pode iniciar a API e fazer perguntas sobre os documentos!")

