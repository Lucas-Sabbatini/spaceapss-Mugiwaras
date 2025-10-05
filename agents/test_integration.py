"""Script de teste para validar a integração com VectorDBManager."""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from packages.api.app.agent.retriever import get_retriever
from packages.api.app.agent.prompts import build_synthesis_prompt


def test_retriever():
    """Testa o retriever com VectorDBManager."""
    print("=" * 60)
    print("TESTE DO RETRIEVER COM VECTORDBMANAGER")
    print("=" * 60)
    
    # Inicializar retriever
    print("\n1. Inicializando retriever...")
    retriever = get_retriever()
    
    if retriever.db_manager is None:
        print("❌ ERRO: VectorDBManager não foi inicializado!")
        return False
    
    print("✅ Retriever inicializado com sucesso")
    
    # Testar query
    print("\n2. Testando query...")
    question = "What are the effects of microgravity on stem cells?"
    
    try:
        results = retriever.retrieve(question, top_k=5)
        print(f"✅ Query executada com sucesso")
        print(f"   - Pergunta: {question}")
        print(f"   - Resultados encontrados: {len(results)}")
        
        if results:
            print("\n   Documentos retornados:")
            for idx, doc in enumerate(results, 1):
                print(f"   [{idx}] {doc}")
        else:
            print("   ⚠️ Nenhum documento encontrado (banco vazio?)")
        
    except Exception as e:
        print(f"❌ ERRO na query: {e}")
        return False
    
    # Testar construção de prompt
    print("\n3. Testando construção de prompt...")
    try:
        prompt = build_synthesis_prompt(question, results)
        print("✅ Prompt construído com sucesso")
        print(f"   - Tamanho do prompt: {len(prompt)} caracteres")
        print("\n   Preview do prompt:")
        print("   " + "-" * 56)
        # Mostrar primeiras 500 caracteres
        preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
        for line in preview.split('\n'):
            print(f"   {line}")
        print("   " + "-" * 56)
        
    except Exception as e:
        print(f"❌ ERRO ao construir prompt: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_retriever()
    sys.exit(0 if success else 1)
