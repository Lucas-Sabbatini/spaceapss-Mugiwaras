"""Script para gerar embeddings dos artigos."""

import sys
from pathlib import Path

from packages.api.app.services.embeddings import get_embeddings_service
from packages.api.app.services.logger import get_logger, log_error, log_info
from packages.api.app.services.redis_client import get_redis_client
from packages.ingest.app.utils import build_text_for_embedding, get_samples_dir, load_json_file

logger = get_logger(__name__)


def generate_embeddings():
    """Gera embeddings para todos os artigos no Redis."""
    log_info(logger, "Iniciando geração de embeddings")

    # Conectar ao Redis
    redis_client = get_redis_client()

    if not redis_client.is_connected():
        log_error(logger, "Redis não conectado", Exception("Redis unavailable"))
        print("❌ Erro: Redis não está disponível. Execute 'docker compose up -d' primeiro.")
        print("💡 Dica: Execute primeiro 'python -m packages.ingest.app.load_json'")
        sys.exit(1)

    # Inicializar serviço de embeddings
    try:
        embeddings_service = get_embeddings_service()
    except Exception as e:
        log_error(logger, "Erro ao inicializar serviço de embeddings", e)
        print(f"❌ Erro ao inicializar embeddings: {str(e)}")
        print("💡 Verifique se GOOGLE_API_KEY está configurado no .env")
        sys.exit(1)

    # Listar todos os artigos
    article_ids = redis_client.list_all_keys("article:*")

    if not article_ids:
        print("⚠️  Nenhum artigo encontrado no Redis.")
        print("💡 Execute primeiro: python -m packages.ingest.app.load_json")
        return

    print(f"📚 Encontrados {len(article_ids)} artigos no Redis\n")

    # Processar cada artigo
    success_count = 0
    error_count = 0
    skip_count = 0

    for article_id in article_ids:
        try:
            # Recuperar artigo
            article_data = redis_client.get_article(article_id)

            if not article_data:
                print(f"⚠️  article:{article_id} → Não encontrado")
                error_count += 1
                continue

            # Verificar se já tem embedding
            if "embedding" in article_data and article_data["embedding"]:
                print(f"⏭️  article:{article_id} → Já possui embedding, pulando...")
                skip_count += 1
                continue

            # Construir texto para embedding
            text = build_text_for_embedding(article_data)

            if not text.strip():
                print(f"⚠️  article:{article_id} → Sem texto para gerar embedding")
                error_count += 1
                continue

            # Gerar embedding
            print(f"⏳ article:{article_id} → Gerando embedding...", end=" ")
            embedding = embeddings_service.get_embedding(text)

            # Atualizar no Redis
            success = redis_client.update_embedding(article_id, embedding)

            if success:
                print(f"✅ ({len(embedding)} dims)")
                success_count += 1
            else:
                print("❌ Erro ao salvar")
                error_count += 1

        except Exception as e:
            log_error(logger, "Erro ao processar artigo", e, article_id=article_id)
            print(f"❌ article:{article_id} → {str(e)}")
            error_count += 1

    # Resumo
    print("\n" + "=" * 50)
    print(f"✅ Embeddings gerados: {success_count}")
    print(f"⏭️  Já existentes: {skip_count}")
    print(f"❌ Erros: {error_count}")
    print(f"📊 Total: {len(article_ids)}")
    print("=" * 50)

    log_info(
        logger,
        "Geração de embeddings concluída",
        success=success_count,
        skipped=skip_count,
        errors=error_count,
    )


if __name__ == "__main__":
    generate_embeddings()
