import chromadb
from chromadb.types import Collection
import uuid

def dict_to_string(retrieval:dict):
    return retrieval["source"]

def string_to_dict(source_string:dict):
    return {"source": source_string}

class VectorDBManager:
    """
    Uma classe para gerenciar operações com o ChromaDB.

    Atributos:
        collection (Collection): O objeto de coleção do ChromaDB.
    """

    def __init__(self):
        chroma_client = chromadb.PersistentClient(path="../../chroma_db")
        
        self.collection: Collection = chroma_client.get_or_create_collection(name="nasa_space_collection")

    def add_document(self, document: str, text: str):
        metadata = string_to_dict(text)
        self.collection.upsert(
            documents=[document],
            metadatas=[metadata],
            ids= str(uuid.uuid4())
        )
        print(f"Documento adicionado/atualizado.")

    def query(self, query_text: str, n_results: int = 2) -> dict:
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        resultFormated = []
        metadatas_list = results["metadatas"][0] 
        resultFormated = list(map(dict_to_string,metadatas_list))
        return resultFormated

if __name__ == "__main__":
    db_manager = VectorDBManager()

    db_manager.add_document(
        document="This is a document about pineapple",
        text="fruit_handbook"
        )
    db_manager.add_document(
        document="This is a document about oranges",
        text="fruit_handbook"
    )

    search_results = db_manager.query(
        query_text="This is a query document about florida",
        n_results=2
    )

    print("\nResultados da Query:")
    print(search_results)