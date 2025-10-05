import pandas as pd
import asyncio
import json


from extract.extractor import extract_url
from extract.sectionizer import sectionize_text
from packages.api.app.services.vector_db import VectorDBManager

# --- Configuração de Caminhos ---
CSV_FILE_PATH = 'shared/SB_publication_PMC.csv'
OUTPUT_JSONL_PATH = 'shared/extracted_data.jsonl'

# --- Função Principal (Atualizada) ---
async def main():
    """
    Função principal que orquestra a leitura do CSV, extração e armazenamento.
    """
    print("Inicializando o banco de dados vetorial...")
    db = VectorDBManager()
    print("Banco de dados pronto.")

    with open(OUTPUT_JSONL_PATH, 'w', encoding='utf-8') as f_out:
        pass 

    try:
        df = pd.read_csv(CSV_FILE_PATH)
    except FileNotFoundError:
        print(f"[ERRO] O arquivo CSV não foi encontrado em: '{CSV_FILE_PATH}'")
        return
        
    articles_added = 0
    print(f"\nIniciando extração de {len(df)} artigos...")

    for index, row in df.iterrows():
        title = row.get('Title', 'Sem Título')
        url = row.get('Link')
        
        print(f"\n({index + 1}/{len(df)}) Processando: {title[:70]}...")
        
        if not url:
            print("  [AVISO] URL não encontrada. Pulando.")
            continue
            
        try:
            # --- MUDANÇA PRINCIPAL AQUI ---
            # Extrai o ID único do artigo a partir do final da URL.
            # Exemplo: '.../articles/PMC4136787/' -> 'PMC4136787'
            doc_id = url.strip('/').split('/')[-1]
            if not doc_id:
                # Se, por algum motivo, a extração falhar, usa a URL completa como fallback.
                doc_id = url
            # --- FIM DA MUDANÇA ---

            text_content, source_type = await extract_url(url)
            
            if text_content and len(text_content.strip()) > 100:
                sections = sectionize_text(text_content)
                abstract = sections.get("abstract", "")
                content = sections.get("content", "")
                
                raw_data = {"url": url, "sections": sections}
                with open(OUTPUT_JSONL_PATH, 'a', encoding='utf-8') as f_out:
                    f_out.write(json.dumps(raw_data, ensure_ascii=False) + '\n')
                
                if abstract and content:
                    document_to_vectorize = abstract
                    
                    escaped_title = title.replace("'", "\\'")
                    escaped_content = content.replace("'", "\\'").replace("\n", " ").replace('"', '\\"')
                    
                    metadata_string = f"'title': '{escaped_title}', 'url': '{url}', 'content': '{escaped_content}'"

                    # Passa o ID extraído da URL para a função add_document
                    db.add_document_id(
                        document=document_to_vectorize, 
                        text=metadata_string, 
                        doc_id=doc_id
                    )
                    
                    articles_added += 1
                else:
                    print("  [AVISO] Abstract ou conteúdo principal não encontrado. Pulando inserção no DB.")
            else:
                print(f"  [AVISO] Extração resultou em conteúdo vazio ou muito curto. Pulando.")
            
            await asyncio.sleep(1)

        except Exception as e:
            print(f"  [ERRO FATAL] ao processar a URL {url}: {e}")
    
    print("\n--- Processo de extração finalizado! ---")
    print(f"Total de documentos adicionados/atualizados no banco de dados: {articles_added}")
    print(f"Um backup com os dados brutos foi salvo em: '{OUTPUT_JSONL_PATH}'")

if __name__ == "__main__":
    asyncio.run(main())