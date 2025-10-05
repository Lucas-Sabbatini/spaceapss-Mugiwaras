"""
Pipeline completo: Scraping + Embeddings + Cosmos DB
Processa artigos, gera embeddings com Google Gemini e salva no Cosmos DB
"""

import asyncio
import json
import os
from typing import List, Dict, Any
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
from azure.cosmos import CosmosClient, PartitionKey

# Imports do projeto
from extract.extractor import extract_url
from extract.sectionizer import sectionize_text

# Carregar .env
load_dotenv()

# Configurações
CSV_FILE_PATH = 'shared/SB_publication_PMC.csv'
OUTPUT_JSONL_PATH = 'shared/extracted_data_with_embeddings.jsonl'

# Google Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_EMBED_MODEL = os.getenv('GOOGLE_EMBED_MODEL', 'models/text-embedding-004')

# Cosmos DB
COSMOS_ENDPOINT = os.getenv('COSMOS_ENDPOINT')
COSMOS_KEY = os.getenv('COSMOS_KEY')
COSMOS_DATABASE = os.getenv('COSMOS_DATABASE', 'cosmos27818-db')
COSMOS_CONTAINER = os.getenv('COSMOS_CONTAINER', 'cosmos27818-container')

# Configurar Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(f"✅ Google Gemini configurado: {GOOGLE_EMBED_MODEL}")
else:
    print("⚠️  GOOGLE_API_KEY não configurado - embeddings não serão gerados")


def generate_embedding(text: str) -> List[float]:
    """
    Gera embedding usando Google Gemini.
    
    Args:
        text: Texto para gerar embedding
        
    Returns:
        Lista de floats representando o embedding (768 dimensões)
    """
    if not GOOGLE_API_KEY:
        return []
    
    try:
        # Limitar tamanho do texto (Gemini tem limite)
        max_chars = 10000
        if len(text) > max_chars:
            text = text[:max_chars]
        
        result = genai.embed_content(
            model=GOOGLE_EMBED_MODEL,
            content=text,
            task_type="retrieval_document"
        )
        
        return result['embedding']
    
    except Exception as e:
        print(f"❌ Erro ao gerar embedding: {e}")
        return []


async def process_article(row: pd.Series, idx: int, total: int) -> Dict[str, Any]:
    """
    Processa um artigo: extrai conteúdo, secciona e gera embedding.
    
    Args:
        row: Linha do DataFrame com dados do artigo
        idx: Índice atual
        total: Total de artigos
        
    Returns:
        Dicionário com dados do artigo + embedding
    """
    url = row.get('URL') or row.get('url') or row.get('Link')
    title = row.get('Title') or row.get('title', 'Sem título')
    
    print(f"\n[{idx+1}/{total}] 📄 Processando: {title[:60]}...")
    print(f"   URL: {url}")
    
    if not url or pd.isna(url):
        print("   ⚠️  Sem URL, pulando...")
        return None
    
    try:
        # 1. Extrair conteúdo
        print("   🔍 Extraindo conteúdo...")
        full_text, source_type = await extract_url(url)
        
        if not full_text or len(full_text) < 50:
            print(f"   ❌ Conteúdo muito curto ou vazio")
            return None
        
        print(f"   ✅ Extraído: {len(full_text)} caracteres (tipo: {source_type})")
        
        # 2. Seccionar texto
        print("   📑 Seccionando texto...")
        sections = sectionize_text(full_text)
        
        # Extrair abstract e conteúdo
        abstract = sections.get('abstract', '')
        if not abstract:
            # Pegar primeiros parágrafos como abstract
            paragraphs = full_text.split('\n\n')
            abstract = paragraphs[0] if paragraphs else ''
        
        content = sections.get('introduction', '') + '\n\n' + sections.get('methods', '')
        if not content.strip():
            content = full_text
        
        # 3. Preparar texto para embedding (combinação otimizada)
        embedding_text = f"{title}\n\n{abstract}\n\n{content[:2000]}"
        
        print(f"   🧮 Gerando embedding...")
        embedding = generate_embedding(embedding_text)
        
        if not embedding:
            print("   ⚠️  Embedding não gerado")
        else:
            print(f"   ✅ Embedding gerado: {len(embedding)} dimensões")
        
        # 4. Extrair keywords do texto
        keywords = []
        common_keywords = [
            'space', 'radiation', 'astronaut', 'microgravity', 'ISS',
            'cosmic', 'solar', 'mars', 'moon', 'satellite', 'orbit',
            'NASA', 'ESA', 'spacecraft', 'mission'
        ]
        
        text_lower = full_text.lower()
        for keyword in common_keywords:
            if keyword.lower() in text_lower:
                keywords.append(keyword)
        
        # 5. Preparar documento
        doc_id = f"article-{idx+1}"
        document = {
            'id': doc_id,
            'pk': doc_id,  # Partition key
            'doc_id': doc_id,
            'title': title,
            'abstract': abstract[:1000] if abstract else '',  # Limitar tamanho
            'content': content[:5000] if content else '',  # Limitar tamanho
            'full_text': full_text[:10000],  # Texto completo limitado
            'url': url,
            'source_type': source_type,
            'keywords': keywords,
            'sections': list(sections.keys()),
            'char_count': len(full_text),
            'has_embedding': len(embedding) > 0
        }
        
        # Adicionar embedding se gerado
        if embedding:
            document['embedding'] = embedding
        
        print(f"   ✅ Documento preparado (id: {doc_id})")
        return document
    
    except Exception as e:
        print(f"   ❌ Erro ao processar: {e}")
        return None


async def main():
    """Função principal do pipeline."""
    print("=" * 80)
    print("🚀 PIPELINE: SCRAPING + EMBEDDINGS + COSMOS DB")
    print("=" * 80)
    print()
    
    # Verificar configurações
    if not GOOGLE_API_KEY:
        print("⚠️  AVISO: GOOGLE_API_KEY não configurado")
        print("   Embeddings NÃO serão gerados!")
        print()
    
    # Conectar ao Cosmos DB (se configurado)
    cosmos_client = None
    container = None
    
    if COSMOS_ENDPOINT and COSMOS_KEY:
        try:
            print(f"📊 Conectando ao Cosmos DB...")
            cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
            database = cosmos_client.get_database_client(COSMOS_DATABASE)
            container = database.get_container_client(COSMOS_CONTAINER)
            print(f"✅ Conectado: {COSMOS_DATABASE}/{COSMOS_CONTAINER}")
            print()
        except Exception as e:
            print(f"⚠️  Erro ao conectar Cosmos DB: {e}")
            print("   Documentos serão salvos apenas em JSONL")
            print()
    else:
        print("⚠️  Cosmos DB não configurado")
        print("   Documentos serão salvos apenas em JSONL")
        print()
    
    # Ler CSV
    print(f"📂 Lendo CSV: {CSV_FILE_PATH}")
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        total = len(df)
        print(f"✅ {total} artigos encontrados")
        print()
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {CSV_FILE_PATH}")
        return
    
    # Processar artigos
    documents = []
    
    # Processar TODOS os artigos (remover limite para processar tudo)
    # df = df.head(3)  # Comentado - processar todos
    
    for idx, row in df.iterrows():
        document = await process_article(row, idx, total)
        
        if document:
            documents.append(document)
            
            # Salvar no Cosmos DB se conectado
            if container:
                try:
                    container.upsert_item(document)
                    print(f"   💾 Salvo no Cosmos DB")
                except Exception as e:
                    print(f"   ⚠️  Erro ao salvar no Cosmos: {e}")
        
        # Delay para não sobrecarregar APIs
        await asyncio.sleep(1)
    
    # Salvar JSONL
    print()
    print(f"💾 Salvando resultados em: {OUTPUT_JSONL_PATH}")
    
    with open(OUTPUT_JSONL_PATH, 'w', encoding='utf-8') as f:
        for doc in documents:
            # Remover embedding do JSONL (muito grande)
            doc_copy = doc.copy()
            if 'embedding' in doc_copy:
                doc_copy['embedding'] = f"[{len(doc['embedding'])} dimensions]"
            f.write(json.dumps(doc_copy, ensure_ascii=False) + '\n')
    
    print(f"✅ {len(documents)} documentos salvos")
    
    # Estatísticas
    print()
    print("=" * 80)
    print("📊 ESTATÍSTICAS")
    print("=" * 80)
    print(f"Total processado:       {len(documents)}/{total}")
    print(f"Com embeddings:         {sum(1 for d in documents if d.get('has_embedding'))}")
    print(f"Salvos no Cosmos DB:    {len(documents) if container else 0}")
    print(f"Salvos em JSONL:        {len(documents)}")
    
    if documents:
        avg_chars = sum(d['char_count'] for d in documents) / len(documents)
        print(f"Média de caracteres:    {avg_chars:.0f}")
    
    print()
    print("🎉 Pipeline concluído!")


if __name__ == "__main__":
    asyncio.run(main())
