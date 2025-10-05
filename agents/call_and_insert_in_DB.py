"""
Script de exemplo para usar o pipeline de enriquecimento.

Este script demonstra como usar o pipeline para processar artigos PMC.
"""

import asyncio
import os
from dotenv import load_dotenv
from extract.enrichment_pipeline import (
    EnrichmentPipeline,
    process_single_article,
    process_from_csv
)

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NCBI_EMAIL = "lucass@example.com"  # Substitua pelo seu email
MONGODB_URI = "mongodb://localhost:27017/"  # Ou seu MongoDB Atlas URI


async def example_single_article():
    """Exemplo: processar um único artigo."""
    print("=" * 60)
    print("EXEMPLO 1: Processar um único artigo")
    print("=" * 60)
    
    # Pode ser URL completa ou apenas PMCID
    pmc_url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2998437/"
    # ou simplesmente: pmc_url = "PMC2998437"
    
    article = await process_single_article(
        pmc_url=pmc_url,
        google_api_key=GOOGLE_API_KEY,
        ncbi_email=NCBI_EMAIL,
        mongodb_uri=MONGODB_URI
    )
    
    if article:
        print("\n✓ Artigo processado com sucesso!")
        print(f"Título: {article.title}")
        print(f"Autores: {', '.join(article.authors[:3])}...")
        print(f"Objetivos: {article.objectives}")
        print(f"Organismos: {article.organisms}")
    else:
        print("\n✗ Falha ao processar artigo")


async def example_batch_processing():
    """Exemplo: processar lista de artigos."""
    print("=" * 60)
    print("EXEMPLO 2: Processar batch de artigos")
    print("=" * 60)
    
    # Lista de PMCIDs ou URLs
    pmc_list = [
        "PMC2998437",
        "PMC3242767",
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3067220/",
        "PMC3251573",
    ]
    
    pipeline = EnrichmentPipeline(
        google_api_key=GOOGLE_API_KEY,
        ncbi_email=NCBI_EMAIL,
        mongodb_uri=MONGODB_URI
    )
    
    await pipeline.process_batch(pmc_list, delay=1.0)


async def example_csv_processing():
    """Exemplo: processar artigos de CSV."""
    print("=" * 60)
    print("EXEMPLO 3: Processar artigos do CSV")
    print("=" * 60)
    
    await process_from_csv(
        csv_path="shared/SB_publication_PMC.csv",
        google_api_key=GOOGLE_API_KEY,
        ncbi_email=NCBI_EMAIL,
        mongodb_uri=MONGODB_URI
    )


async def example_query_database():
    """Exemplo: consultar dados do banco."""
    from extract.enrichment_pipeline import DatabaseManager
    
    print("=" * 60)
    print("EXEMPLO 4: Consultar banco de dados")
    print("=" * 60)
    
    db = DatabaseManager(MONGODB_URI)
    
    # Contar artigos
    total = db.count_articles()
    print(f"\nTotal de artigos no banco: {total}")
    
    # Buscar um artigo específico
    article = db.get_article("PMC2998437")
    
    if article:
        print(f"\nArtigo encontrado:")
        print(f"  Título: {article['title']}")
        print(f"  Ano: {article['year']}")
        print(f"  Objetivos: {article['objectives']}")
        print(f"  Métodos: {article['methods']}")
        print(f"  Organismos: {article['organisms']}")
        print(f"  Achados: {article['significant_findings']}")


def main():
    """Menu principal."""
    print("\n" + "=" * 60)
    print("PIPELINE DE ENRIQUECIMENTO DE ARTIGOS PMC")
    print("=" * 60)
    print("\nEscolha uma opção:")
    print("1. Processar um único artigo")
    print("2. Processar batch de artigos")
    print("3. Processar CSV completo")
    print("4. Consultar banco de dados")
    print("0. Sair")
    
    choice = input("\nOpção: ").strip()
    
    if choice == "1":
        asyncio.run(example_single_article())
    elif choice == "2":
        asyncio.run(example_batch_processing())
    elif choice == "3":
        asyncio.run(example_csv_processing())
    elif choice == "4":
        asyncio.run(example_query_database())
    elif choice == "0":
        print("Saindo...")
    else:
        print("Opção inválida!")


if __name__ == "__main__":
    # Verificar se API key está configurada
    if not GOOGLE_API_KEY:
        print("ERRO: GOOGLE_API_KEY não encontrada no .env")
        print("Adicione: GOOGLE_API_KEY=sua_chave_aqui")
        exit(1)
    
    main()
