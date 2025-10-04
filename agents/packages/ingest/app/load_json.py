"""Script para carregar artigos no Redis."""

import sys
from pathlib import Path

from packages.api.app.services.logger import get_logger, log_error, log_info
from packages.api.app.services.redis_client import get_redis_client
from packages.ingest.app.utils import get_samples_dir, load_json_file

logger = get_logger(__name__)


def load_samples_to_redis():
    """Carrega todos os samples JSON no Redis."""
    log_info(logger, "Iniciando carregamento de samples no Redis")

    # Conectar ao Redis
    redis_client = get_redis_client()

    if not redis_client.is_connected():
        log_error(logger, "Redis não conectado", Exception("Redis unavailable"))
        print("❌ Erro: Redis não está disponível. Execute 'docker compose up -d' primeiro.")
        sys.exit(1)

    # Buscar arquivos JSON
    samples_dir = get_samples_dir()
    if not samples_dir.exists():
        log_error(logger, "Pasta de samples não encontrada", Exception(), path=samples_dir)
        print(f"❌ Erro: Pasta {samples_dir} não encontrada.")
        sys.exit(1)

    json_files = list(samples_dir.glob("*.json"))
    if not json_files:
        log_info(logger, "Nenhum arquivo JSON encontrado", path=samples_dir)
        print(f"⚠️  Nenhum arquivo JSON encontrado em {samples_dir}")
        return

    # Carregar cada arquivo
    success_count = 0
    error_count = 0

    for json_file in json_files:
        try:
            article_data = load_json_file(json_file)
            article_id = article_data.get("id")

            if not article_id:
                log_error(logger, "Artigo sem ID", Exception(), file=json_file.name)
                print(f"⚠️  {json_file.name}: Artigo sem campo 'id', pulando...")
                error_count += 1
                continue

            # Salvar no Redis
            success = redis_client.set_article(article_id, article_data)

            if success:
                print(f"✅ {json_file.name} → article:{article_id}")
                success_count += 1
            else:
                print(f"❌ {json_file.name} → Erro ao salvar")
                error_count += 1

        except Exception as e:
            log_error(logger, "Erro ao processar arquivo", e, file=json_file.name)
            print(f"❌ {json_file.name} → {str(e)}")
            error_count += 1

    # Resumo
    print("\n" + "=" * 50)
    print(f"✅ Sucesso: {success_count}")
    print(f"❌ Erros: {error_count}")
    print(f"📊 Total: {len(json_files)}")
    print("=" * 50)

    log_info(logger, "Carregamento concluído", success=success_count, errors=error_count)


if __name__ == "__main__":
    load_samples_to_redis()
