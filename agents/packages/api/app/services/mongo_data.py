import os
import re
import sys
import time
from typing import List, Dict, Any
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel
import google.generativeai as genai
from pathlib import Path

# Import ArticleMetadata - ajustar sys.path e importar
# Adicionar o diretório agents ao sys.path se necessário
agents_path = Path(__file__).parent.parent.parent.parent.parent
if str(agents_path) not in sys.path:
    sys.path.insert(0, str(agents_path))

# Agora importar ArticleMetadata
try:
    from extract.models import ArticleMetadata
except ImportError as e:
    print(f"⚠ Erro ao importar ArticleMetadata: {e}")
    print(f"⚠ sys.path: {sys.path}")
    print(f"⚠ agents_path: {agents_path}")
    raise


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBED_MODEL", "models/text-embedding-004")

# Configurar Google Generative AI
if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY não configurado. "
        "Defina GOOGLE_API_KEY no arquivo .env"
    )

genai.configure(api_key=GOOGLE_API_KEY)

class MongoDataManager:
    """
    Classe para gerenciar operações com MongoDB e embeddings do Google Generative AI.
    
    Armazena artigos científicos e permite busca vetorial usando embeddings gerados
    pela API do Google Generative AI.
    """

    def __init__(self, endpoint: str = None, key: str = None, database_name: str = None, container_name: str = None):
        """
        Inicializa o gerenciador MongoDB.
        
        Args:
            endpoint: Endpoint MongoDB (opcional, usa env var)
            key: Não utilizado (mantido para compatibilidade)
            database_name: Nome do database (opcional, usa env var)
            container_name: Nome da collection (opcional, usa env var)
        """
        # Obter configurações de variáveis de ambiente ou parâmetros
        self.endpoint = endpoint or os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.database_name = database_name or os.getenv("MONGODB_DATABASE", "spaceapss")
        self.collection_name = container_name or os.getenv("MONGODB_COLLECTION", "articles")
        
        # Conectar ao MongoDB e armazenar cliente e collection como atributos
        self.client = MongoClient(self.endpoint)
        self.collection = self.client[self.database_name][self.collection_name]
        
        # Nome do índice de busca vetorial
        self.index_name = "vector_index"
        
        print(f"✓ MongoDB conectado: {self.database_name}.{self.collection_name}")
        print(f"✓ Usando Google Generative AI para embeddings (modelo: {EMBEDDING_MODEL})")      

    def _get_embedding(self, data: str) -> List[float]:
        """
        Gera embeddings vetoriais para o texto fornecido usando Google Generative AI.
        
        Args:
            data: Texto para gerar embedding
            
        Returns:
            Lista de floats representando o embedding
        """
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=data,
            task_type="retrieval_document"
        )
        return result['embedding']

    def add_document(self, document: ArticleMetadata) -> None:
        """
        Insere um objeto ArticleMetadata no banco de dados vetorial MongoDB, junto com seu embedding.

        Args:
            document: Instância de ArticleMetadata a ser inserida.
        """
        if not document.abstract:
            raise ValueError("Abstract não encontrado, pulando inserção")
        
        embedding = self._get_embedding(document.abstract)

        document_dict = document.to_dict()
        document_dict["embedding"] = embedding

        self.collection.insert_one(document_dict)

    def query(self, query_text: str, n_results: int = 2) -> List[ArticleMetadata]:
        """
        Realiza busca vetorial semântica no banco de dados.
        
        Args:
            query_text: Texto da consulta
            n_results: Número de resultados a retornar (padrão: 2)
            
        Returns:
            Lista de objetos ArticleMetadata ordenados por relevância
        """
        # Gerar embedding da query
        query_embedding = self._get_embedding(query_text)
        
        # Pipeline de agregação para busca vetorial
        pipeline = [
            {
                "$vectorSearch": {
                    "index": self.index_name,
                    "queryVector": query_embedding,
                    "path": "embedding",
                    "exact": True,
                    "limit": n_results
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "embedding": 0  # Excluir embedding dos resultados
                }
            }
        ]
        
        # Executar busca
        results = self.collection.aggregate(pipeline)
        
        # Converter resultados para ArticleMetadata
        articles = []
        for doc in results:
            try:
                article = ArticleMetadata.from_dict(doc)
                articles.append(article)
            except Exception as e:
                print(f"⚠ Erro ao converter documento: {e}")
                continue
        
        return articles
    
    def create_vector_index(self, num_dimensions: int = 768):
        """
        Cria o índice de busca vetorial no MongoDB.
        
        Args:
            num_dimensions: Número de dimensões do embedding (padrão: 768)
        """
        # Criar modelo do índice
        search_index_model = SearchIndexModel(
            definition={
                "fields": [
                    {
                        "type": "vector",
                        "numDimensions": num_dimensions,
                        "path": "embedding",
                        "similarity": "cosine"
                    }
                ]
            },
            name=self.index_name,
            type="vectorSearch"
        )
        
        # Criar índice
        self.collection.create_search_index(model=search_index_model)
        
        # Aguardar índice ficar pronto
        print(f"Aguardando índice {self.index_name} ficar pronto...")
        
        def is_queryable(index):
            return index.get("queryable") is True
        
        while True:
            indices = list(self.collection.list_search_indexes(self.index_name))
            if len(indices) and is_queryable(indices[0]):
                break
            time.sleep(5)
        
        print(f"✓ Índice {self.index_name} pronto para consultas!")

    def get_total_documents(self) -> int:
        """
        Retorna o número total de documentos na coleção.
        
        Returns:
            Número total de documentos
        """
        return self.collection.count_documents({})
