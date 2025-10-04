"""Utilitários para ingestão."""

import json
from pathlib import Path
from typing import Any, Dict


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Carrega arquivo JSON."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file(file_path: Path, data: Dict[str, Any]) -> None:
    """Salva dados em arquivo JSON."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_samples_dir() -> Path:
    """Retorna caminho da pasta de samples."""
    return Path(__file__).parent.parent / "data" / "samples"


def build_text_for_embedding(article: Dict[str, Any]) -> str:
    """
    Constrói texto para gerar embedding.
    
    Combina: título + abstract + primeiras seções
    """
    parts = []

    # Título
    if title := article.get("title"):
        parts.append(title)

    # Abstract
    if abstract := article.get("abstract"):
        parts.append(abstract)

    # Seções (primeiras 3)
    if sections := article.get("sections"):
        for section in sections[:3]:
            heading = section.get("heading", "")
            content = section.get("content", "")[:500]  # Limitar conteúdo
            parts.append(f"{heading}: {content}")

    return "\n\n".join(parts)
