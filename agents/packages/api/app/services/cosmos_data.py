"""Gerenciador de banco de dados usando Azure Cosmos DB (SQL API)."""

import os
import re
from typing import List, Dict, Any
from azure.cosmos import CosmosClient, PartitionKey, exceptions


class CosmosDataManager:
    """
    Classe para gerenciar operações com Azure Cosmos DB (SQL API).
    
    Armazena artigos científicos e permite busca por palavras-chave.
    """

    def __init__(self, endpoint: str = None, key: str = None, database_name: str = None, container_name: str = None):
        """
        Inicializa o gerenciador do Cosmos DB.
        
        Args:
            endpoint: Endpoint do Cosmos DB (opcional, usa env var)
            key: Primary key (opcional, usa env var)
            database_name: Nome do database (opcional, usa env var)
            container_name: Nome do container (opcional, usa env var)
        """
        # Obter configurações de variáveis de ambiente ou parâmetros
        self.endpoint = endpoint or os.getenv("COSMOS_ENDPOINT")
        self.key = key or os.getenv("COSMOS_KEY")
        self.database_name = database_name or os.getenv("COSMOS_DATABASE", "spaceapss")
        self.container_name = container_name or os.getenv("COSMOS_CONTAINER", "articles")
        
        if not self.endpoint or not self.key:
            raise ValueError(
                "Cosmos DB endpoint e key não configurados. "
                "Defina COSMOS_ENDPOINT e COSMOS_KEY ou passe como parâmetros."
            )
        
        # Conectar ao Cosmos DB
        try:
            self.client = CosmosClient(self.endpoint, self.key)
            print("✅ Conectado ao Azure Cosmos DB!")
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            raise
        
        # Criar/obter database e container
        try:
            self.database = self.client.get_database_client(self.database_name)
            self.container = self.database.get_container_client(self.container_name)
            print(f"✅ Database: {self.database_name}")
            print(f"✅ Container: {self.container_name}")
            print(f"   Total de documentos: {self.get_total_documents()}")
        except exceptions.CosmosResourceNotFoundError:
            print(f"❌ Database ou Container não encontrado!")
            raise

    def add_document(self, document: str, text: str) -> None:
        """
        Adiciona um documento no Cosmos DB.
        
        Args:
            document: Conteúdo do documento (abstract)
            text: Metadados em formato string
        """
        import uuid
        doc_id = str(uuid.uuid4())
        self.add_document_id(document, text, doc_id)

    def add_document_id(self, document: str, text: str, doc_id: str) -> None:
        """
        Adiciona ou atualiza um documento com ID específico.
        
        Args:
            document: Conteúdo do documento (abstract)
            text: Metadados em formato string 'title': '...', 'url': '...', 'content': '...'
            doc_id: ID único do documento (ex: PMC4136787)
        """
        # Parse dos metadados
        metadata = self._parse_metadata_string(text)
        
        # Criar documento
        doc = {
            'id': doc_id,
            'pk': doc_id,  # Partition key
            'doc_id': doc_id,
            'abstract': document,
            'title': metadata.get('title', ''),
            'url': metadata.get('url', ''),
            'content': metadata.get('content', ''),
            'keywords': self._extract_keywords(document, metadata.get('title', ''))
        }
        
        # Inserir ou atualizar (upsert)
        try:
            self.container.upsert_item(body=doc)
            print(f"✅ Documento {doc_id} adicionado/atualizado no Cosmos DB.")
        except Exception as e:
            print(f"❌ Erro ao salvar documento {doc_id}: {e}")

    def _extract_keywords(self, abstract: str, title: str) -> List[str]:
        """Extrai palavras-chave do documento."""
        text = f"{title} {abstract}".lower()
        
        words = set()
        for word in text.split():
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) >= 4:
                words.add(clean_word)
        
        return sorted(words)

    def query(self, query_text: str, n_results: int = 2) -> List[str]:
        """
        Busca documentos por palavras-chave (compatibilidade com API antiga).
        """
        results = self.query_with_metadata(query_text, n_results)
        
        formatted = []
        for result in results:
            metadata_str = f"'title': '{result['title']}', 'url': '{result['url']}', 'content': '{result['content']}'"
            formatted.append(metadata_str)
        
        return formatted

    def query_with_metadata(self, query_text: str, n_results: int = 2) -> List[Dict[str, Any]]:
        """
        Busca documentos por palavras-chave retornando metadados estruturados.
        """
        # Extrair palavras-chave da query
        query_lower = query_text.lower()
        words = []
        for word in query_lower.split():
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) >= 4:
                words.append(clean_word)
        
        if not words:
            return self._get_random_articles(n_results)
        
        # Buscar documentos que contêm as palavras
        try:
            # Query SQL do Cosmos DB
            query = f"SELECT * FROM c WHERE ARRAY_LENGTH(c.keywords) > 0 OFFSET 0 LIMIT {n_results * 10}"
            
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            # Calcular score para cada documento
            doc_scores = []
            for item in items:
                keywords_set = set(item.get('keywords', []))
                score = sum(1 for word in words if word in keywords_set)
                
                if score > 0:
                    doc_scores.append({
                        'item': item,
                        'score': score / len(words)
                    })
            
            # Se não encontrou nada, retornar aleatórios
            if not doc_scores:
                return self._get_random_articles(n_results)
            
            # Ordenar por score
            doc_scores.sort(key=lambda x: x['score'], reverse=True)
            
            # Pegar top N
            top_docs = doc_scores[:n_results]
            
            # Formatar resultados
            results = []
            for doc in top_docs:
                item = doc['item']
                score = doc['score']
                
                results.append({
                    'id': item.get('doc_id', item.get('id', '')),
                    'document': item.get('abstract', ''),
                    'title': item.get('title', 'Unknown Title'),
                    'url': item.get('url', ''),
                    'content': item.get('content', ''),
                    'distance': 1.0 - score,
                    'score': score
                })
            
            return results
            
        except Exception as e:
            print(f"⚠️  Erro na busca: {e}. Retornando artigos aleatórios.")
            return self._get_random_articles(n_results)

    def _get_random_articles(self, n: int) -> List[Dict[str, Any]]:
        """Retorna N artigos aleatórios."""
        try:
            query = f"SELECT TOP {n} * FROM c"
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            results = []
            for item in items:
                results.append({
                    'id': item.get('doc_id', item.get('id', '')),
                    'document': item.get('abstract', ''),
                    'title': item.get('title', 'Unknown Title'),
                    'url': item.get('url', ''),
                    'content': item.get('content', ''),
                    'distance': 1.0,
                    'score': 0.0
                })
            
            return results
        except Exception:
            return []

    def _parse_metadata_string(self, metadata_str: str) -> Dict[str, str]:
        """Parse metadata string."""
        result = {
            'title': '',
            'url': '',
            'content': ''
        }
        
        title_match = re.search(r"'title':\s*'([^']*)'", metadata_str)
        if title_match:
            result['title'] = title_match.group(1).replace("\\'", "'")
        
        url_match = re.search(r"'url':\s*'([^']*)'", metadata_str)
        if url_match:
            result['url'] = url_match.group(1)
        
        content_match = re.search(r"'content':\s*'(.*)'$", metadata_str)
        if content_match:
            result['content'] = content_match.group(1).replace("\\'", "'").replace('\\"', '"')
        
        return result

    def get_total_documents(self) -> int:
        """Retorna o número total de documentos armazenados."""
        try:
            query = "SELECT VALUE COUNT(1) FROM c"
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            return items[0] if items else 0
        except Exception as e:
            print(f"Erro ao contar documentos: {e}")
            return 0


# Teste
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testando CosmosDataManager...")
    
    try:
        db = CosmosDataManager()
        print(f"\nTotal de documentos: {db.get_total_documents()}")
        
        # Testar busca se houver documentos
        if db.get_total_documents() > 0:
            results = db.query_with_metadata("space radiation effects", n_results=3)
            print(f"\nResultados da busca:")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']} (score: {result['score']:.2f})")
    except Exception as e:
        print(f"❌ Erro: {e}")
