"""Gerenciador de banco de dados vetorial usando ChromaDB."""

import chromadb
from chromadb.types import Collection
import uuid


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

    def __init__(self, db_path: str = "../../../chroma_db"):
        """
        Inicializa o gerenciador do banco de dados vetorial.
        
        Args:
            db_path: Caminho para o diretório do ChromaDB
        """
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

