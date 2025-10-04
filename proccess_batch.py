import pandas as pd
import asyncio
import json
import sqlite3
import sys

# Adiciona a pasta 'api' ao caminho do Python para que as importações funcionem
sys.path.append('api')
from extract.extractor import extract_url
from shared.sectionizer import sectionize_text

# --- Configuração de Caminhos ---
CSV_FILE_PATH = 'api/shared/SB_publication_PMC.csv'
DB_FILE_PATH = 'api/shared/articles.db'
# --- MUDANÇA AQUI: Alterado o nome do ficheiro de backup para .jsonl ---
OUTPUT_JSONL_PATH = 'api/shared/extracted_data.jsonl'

# --- Funções do Banco de Dados (sem alteração) ---
def setup_database():
    """Cria a tabela no banco de dados SQLite se ela não existir."""
    print(f"Verificando e configurando o banco de dados em '{DB_FILE_PATH}'...")
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            abstract TEXT,
            content TEXT,
            url TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Banco de dados pronto.")

def insert_article(title, abstract, content, url):
    """Insere um artigo no banco de dados, evitando duplicatas pela URL."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO articles (title, abstract, content, url) VALUES (?, ?, ?, ?)",
            (title, abstract, content, url)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# --- Função Principal ---
async def main():
    """Função principal que orquestra a leitura do CSV, extração e armazenamento."""
    setup_database()
    
    # --- MUDANÇA AQUI: Abre o ficheiro de backup no início e apaga o conteúdo antigo ---
    with open(OUTPUT_JSONL_PATH, 'w', encoding='utf-8') as f_out:
        pass # Apenas para limpar o ficheiro se ele já existir

    try:
        df = pd.read_csv(CSV_FILE_PATH)
    except FileNotFoundError:
        print(f"[ERRO] O arquivo CSV não foi encontrado em: '{CSV_FILE_PATH}'")
        print("Verifique se o arquivo está na pasta 'api/shared/'.")
        return
        
    articles_added = 0
    print(f"\nIniciando extração de {len(df)} artigos. Isso pode levar vários minutos...")

    for index, row in df.iterrows():
        title = row.get('Title', 'Sem Título')
        url = row.get('Link')
        
        print(f"\n({index + 1}/{len(df)}) Processando: {title[:70]}...")
        
        if not url:
            print("  [AVISO] URL não encontrada. Pulando.")
            continue
            
        try:
            text_content, source_type = await extract_url(url)
            
            if text_content and len(text_content.strip()) > 100:
                sections = sectionize_text(text_content)
                abstract = sections.get("abstract", "")
                content = sections.get("content", "")
                
                # --- MUDANÇA AQUI: Escreve no ficheiro de backup a cada iteração ---
                raw_data = {"url": url, "sections": sections}
                with open(OUTPUT_JSONL_PATH, 'a', encoding='utf-8') as f_out:
                    f_out.write(json.dumps(raw_data, ensure_ascii=False) + '\n')
                
                if content:
                    success = insert_article(title, abstract, content, url)
                    if success:
                        print("  [SUCESSO] Artigo inserido no banco de dados.")
                        articles_added += 1
                    else:
                        print("  [INFO] Artigo já existia no banco de dados. Pulando.")
                else:
                    print("  [AVISO] Não foi possível separar o conteúdo principal do abstract. Pulando.")
            else:
                print(f"  [AVISO] Extração resultou em conteúdo vazio ou muito curto. Pulando.")
            
            await asyncio.sleep(1)

        except Exception as e:
            print(f"  [ERRO FATAL] ao processar a URL {url}: {e}")
    
    print("\n--- Processo de extração finalizado! ---")
    print(f"Total de artigos adicionados ao banco de dados: {articles_added}")
    print(f"O banco de dados está salvo em: '{DB_FILE_PATH}'")
    print(f"Um backup com os dados brutos foi salvo em: '{OUTPUT_JSONL_PATH}'")

if __name__ == "__main__":
    asyncio.run(main())