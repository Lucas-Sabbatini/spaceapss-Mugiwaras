"""Gerenciador de banco de dados usando Azure Cosmos DB (SQL API)."""

import os
import re
from typing import List, Dict, Any, Optional
from azure.cosmos import CosmosClient, PartitionKey, exceptions


class CosmosDataManager:
    """
    Classe para gerenciar operações com Azure Cosmos DB (SQL API).
    
    Armazena artigos científicos e permite busca por palavras-chave.
    """

    def __init__(
        self, 
        endpoint: Optional[str] = None, 
        key: Optional[str] = None, 
        database_name: Optional[str] = None, 
        container_name: Optional[str] = None,
        google_api_key: Optional[str] = None,
        google_embed_model: Optional[str] = None
    ):
        """
        Inicializa o gerenciador do Cosmos DB.
        
        Args:
            endpoint: Endpoint do Cosmos DB (opcional, usa env var)
            key: Primary key (opcional, usa env var)
            database_name: Nome do database (opcional, usa env var)
            container_name: Nome do container (opcional, usa env var)
            google_api_key: Google API Key para embeddings (opcional)
            google_embed_model: Modelo de embedding do Google (opcional)
        """
        # Obter configurações de variáveis de ambiente ou parâmetros
        self.endpoint = endpoint or os.getenv("COSMOS_ENDPOINT")
        self.key = key or os.getenv("COSMOS_KEY")
        self.database_name = database_name or os.getenv("COSMOS_DATABASE", "spaceapss")
        self.container_name = container_name or os.getenv("COSMOS_CONTAINER", "articles")
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY", "")
        self.google_embed_model = google_embed_model or os.getenv("GOOGLE_EMBED_MODEL", "models/text-embedding-004")
        # If credentials are missing, mark manager as disabled instead of raising.
        if not self.endpoint or not self.key:
            print("⚠️  Cosmos DB endpoint/key não configurados. CosmosDataManager ficará desabilitado.")
            self.enabled = False
            self.client = None
            self.database = None
            self.container = None
            return

        self.enabled = True
        # Conectar ao Cosmos DB
        try:
            self.client = CosmosClient(self.endpoint, self.key)
            print("✅ Conectado ao Azure Cosmos DB!")
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            # If connection fails, disable manager but do not raise to avoid breaking the app.
            self.enabled = False
            self.client = None
            self.database = None
            self.container = None
            return
        
        # Criar/obter database e container
        try:
            self.database = self.client.get_database_client(self.database_name)
            self.container = self.database.get_container_client(self.container_name)
            print(f"✅ Database: {self.database_name}")
            print(f"✅ Container: {self.container_name}")
            print(f"   Total de documentos: {self.get_total_documents()}")
        except exceptions.CosmosResourceNotFoundError:
            print(f"❌ Database ou Container não encontrado!")
            # If resources are not found, disable manager instead of raising.
            self.enabled = False
            self.client = None
            self.database = None
            self.container = None
            return

    def add_document(self, document: str, text: str) -> None:
        """
        Adiciona um documento no Cosmos DB.
        
        Args:
            document: Conteúdo do documento (abstract)
            text: Metadados em formato string
        """
        if not getattr(self, "enabled", False):
            print("⚠️  CosmosDataManager desabilitado: add_document ignorado.")
            return

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
        
        if not getattr(self, "enabled", False):
            print(f"⚠️  CosmosDataManager desabilitado: upsert {doc_id} ignorado.")
            return

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
        Busca documentos usando vector search se disponível, senão fallback para keyword search.
        """
        if not getattr(self, "enabled", False):
            print("⚠️  CosmosDataManager desabilitado: retornando lista vazia no query_with_metadata.")
            return []

        # Tentar busca vetorial primeiro
        try:
            return self.vector_search(query_text, n_results)
        except Exception as e:
            print(f"⚠️  Vector search falhou: {e}. Usando keyword search...")
            return self._keyword_search(query_text, n_results)

    def vector_search(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca vetorial usando embeddings do Google Gemini.
        
        Args:
            query_text: Texto da query
            n_results: Número de resultados
            
        Returns:
            Lista de documentos ordenados por similaridade
        """
        if not getattr(self, "enabled", False):
            raise Exception("CosmosDataManager desabilitado: não é possível executar vector_search.")

        # Configurar Gemini
        try:
            import google.generativeai as genai
        except Exception as ie:
            raise ImportError("google.generativeai não instalado: instale o pacote necessário para usar vector_search") from ie

        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY não configurada")
        
        genai.configure(api_key=self.google_api_key)
        
        # Gerar embedding da query
        result = genai.embed_content(
            model=self.google_embed_model,
            content=query_text,
            task_type="retrieval_query"
        )
        query_embedding = result['embedding']
        
        # Query vetorial no Cosmos DB
        query_sql = """
        SELECT TOP @topK
            c.id,
            c.doc_id,
            c.title,
            c.abstract,
            c.content,
            c.url,
            c.keywords,
            VectorDistance(c.embedding, @queryVector) AS similarity
        FROM c
        WHERE IS_DEFINED(c.embedding)
        ORDER BY VectorDistance(c.embedding, @queryVector)
        """
        
        items = list(self.container.query_items(
            query=query_sql,
            parameters=[
                {"name": "@topK", "value": n_results},
                {"name": "@queryVector", "value": query_embedding}
            ],
            enable_cross_partition_query=True
        ))
        
        # Formatar resultados
        results = []
        for item in items:
            # Similaridade do Cosmos DB: menor = mais similar
            # Converter para score: maior = melhor
            similarity = item.get('similarity', 1.0)
            score = max(0.0, 1.0 - similarity)  # Score entre 0 e 1
            
            # Extrair ano do título ou metadados se disponível
            year = None
            title = item.get('title', 'Unknown Title')
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', title)
            if year_match:
                year = int(year_match.group())
            
            results.append({
                'id': item.get('doc_id', item.get('id', '')),
                'document': item.get('abstract', ''),
                'title': title,
                'url': item.get('url', ''),
                'content': item.get('content', ''),
                'distance': similarity,
                'score': score,
                'keywords': item.get('keywords', []),
                'year': year
            })
            
            print(f"  📄 {item.get('doc_id', 'unknown')[:15]}: similarity={similarity:.4f}, score={score:.4f}")
        
        return results

    def _keyword_search(self, query_text: str, n_results: int = 2) -> List[Dict[str, Any]]:
        """
        Busca documentos por palavras-chave (fallback method).
        """
        # Extrair palavras-chave da query
        query_lower = query_text.lower()
        words = []
        for word in query_lower.split():
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) >= 4:
                words.append(clean_word)
        
        if not getattr(self, "enabled", False):
            print("⚠️  CosmosDataManager desabilitado: retornando lista vazia no _keyword_search.")
            return []

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
                
                # Extrair ano do título
                year = None
                title = item.get('title', 'Unknown Title')
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', title)
                if year_match:
                    year = int(year_match.group())
                
                results.append({
                    'id': item.get('doc_id', item.get('id', '')),
                    'document': item.get('abstract', ''),
                    'title': title,
                    'url': item.get('url', ''),
                    'content': item.get('content', ''),
                    'distance': 1.0 - score,
                    'score': score,
                    'year': year
                })
            
            return results
            
        except Exception as e:
            print(f"⚠️  Erro na busca: {e}. Retornando artigos aleatórios.")
            return self._get_random_articles(n_results)

    def _get_random_articles(self, n: int) -> List[Dict[str, Any]]:
        """Retorna N artigos aleatórios."""
        if not getattr(self, "enabled", False):
            print("⚠️  CosmosDataManager desabilitado: retornando lista vazia no _get_random_articles.")
            return []

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
        if not getattr(self, "enabled", False):
            return 0

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
