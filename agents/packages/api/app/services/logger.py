"""Configuração de logging."""

import logging
import sys
from typing import Any, Dict

# Configurar formato e handler
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger configurado."""
    return logging.getLogger(name)


def log_info(logger: logging.Logger, message: str, **kwargs: Any) -> None:
    """Log info com contexto adicional."""
    extra = " ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(f"{message} {extra}".strip())


def log_error(logger: logging.Logger, message: str, error: Exception, **kwargs: Any) -> None:
    """Log error com exceção e contexto."""
    extra = " ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.error(f"{message} {extra} error={type(error).__name__}: {str(error)}".strip())


def log_debug(logger: logging.Logger, message: str, data: Dict[str, Any] | None = None) -> None:
    """Log debug com dados estruturados."""
    if data:
        logger.debug(f"{message} data={data}")
    else:
        logger.debug(message)