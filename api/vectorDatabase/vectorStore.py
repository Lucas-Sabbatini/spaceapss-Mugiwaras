import chromadb
from chromadb.types import Collection
import uuid
import ast

def dict_to_string(retrieval:dict):
    return retrieval["source"]

def string_to_dict(source_string: str) -> dict:
    try:
        return ast.literal_eval("{" + source_string + "}")
    except (ValueError, SyntaxError):
        return {"source": source_string}

class VectorDBManager:
    def __init__(self):
        chroma_client = chromadb.PersistentClient(path="api/chroma_db")
        self.collection: Collection = chroma_client.get_or_create_collection(name="nasa_space_collection")

    def add_document(self, abstract: str, document: str, doc_id: str):
        metadata = string_to_dict(document)
        self.collection.upsert(
            documents=[abstract],
            metadatas=[metadata],
            ids=[doc_id]
        )
        print(f"Documento adicionado/atualizado.")

    def query(self, query_text: str, n_results: int = 2) -> dict:
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        resultFormated = []
        metadatas_list = results.get("metadatas", [[]])[0]
        if metadatas_list:
            resultFormated = [item.get('content', '') for item in metadatas_list]
        return resultFormated