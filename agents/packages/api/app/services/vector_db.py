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
