"""
Teste de busca vetorial no Cosmos DB
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
from azure.cosmos import CosmosClient

load_dotenv()

# Configurar
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_EMBED_MODEL = os.getenv('GOOGLE_EMBED_MODEL', 'models/text-embedding-004')
COSMOS_ENDPOINT = os.getenv('COSMOS_ENDPOINT')
COSMOS_KEY = os.getenv('COSMOS_KEY')
COSMOS_DATABASE = os.getenv('COSMOS_DATABASE', 'cosmos27818-db')
COSMOS_CONTAINER = os.getenv('COSMOS_CONTAINER', 'cosmos27818-container')

genai.configure(api_key=GOOGLE_API_KEY)

def generate_query_embedding(query: str):
    """Gera embedding para a query."""
    result = genai.embed_content(
        model=GOOGLE_EMBED_MODEL,
        content=query,
        task_type="retrieval_query"
    )
    return result['embedding']

def vector_search(query: str, top_k: int = 3):
    """Busca vetorial no Cosmos DB."""
    print(f"🔍 Buscando: '{query}'")
    print()
    
    # Gerar embedding da query
    print("🧮 Gerando embedding da query...")
    query_embedding = generate_query_embedding(query)
    print(f"✅ Embedding gerado: {len(query_embedding)} dimensões")
    print()
    
    # Conectar ao Cosmos
    print("📊 Conectando ao Cosmos DB...")
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = client.get_database_client(COSMOS_DATABASE)
    container = database.get_container_client(COSMOS_CONTAINER)
    print("✅ Conectado")
    print()
    
    # Query vetorial
    print(f"🔎 Executando busca vetorial (top {top_k})...")
    
    query_sql = """
    SELECT TOP @topK
        c.id,
        c.title,
        c.abstract,
        c.keywords,
        VectorDistance(c.embedding, @queryVector) AS similarity
    FROM c
    WHERE IS_DEFINED(c.embedding)
    ORDER BY VectorDistance(c.embedding, @queryVector)
    """
    
    results = list(container.query_items(
        query=query_sql,
        parameters=[
            {"name": "@topK", "value": top_k},
            {"name": "@queryVector", "value": query_embedding}
        ],
        enable_cross_partition_query=True
    ))
    
    print(f"✅ {len(results)} resultados encontrados")
    print()
    
    # Mostrar resultados
    print("=" * 80)
    print("📋 RESULTADOS")
    print("=" * 80)
    
    for i, item in enumerate(results, 1):
        print(f"\n{i}. {item['title'][:80]}")
        print(f"   Similarity: {item['similarity']:.4f}")
        print(f"   Keywords: {', '.join(item.get('keywords', []))}")
        print(f"   Abstract: {item['abstract'][:200]}...")
    
    print()
    return results

if __name__ == "__main__":
    # Teste 1: Busca sobre microgravidade
    print("\n" + "=" * 80)
    print("TEST 1: Microgravity effects")
    print("=" * 80)
    vector_search("What are the effects of microgravity on bones?", top_k=3)
    
    # Teste 2: Busca sobre stem cells
    print("\n" + "=" * 80)
    print("TEST 2: Stem cells in space")
    print("=" * 80)
    vector_search("stem cell regeneration in space", top_k=3)
    
    print("\n🎉 Testes concluídos!")
