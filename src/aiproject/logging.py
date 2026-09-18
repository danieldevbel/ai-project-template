"""Logging estruturado.

Em desenvolvimento o log sai legivel no terminal; em producao sai em JSON,
pronto para ser coletado por Loki, CloudWatch ou equivalente.
"""

from __future__ import annotations

import logging
import sys

import structlog

from aiproject.settings import Settings


def configure_logging(settings: Settings) -> None:
    """Configura o structlog de acordo com o ambiente."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )

    processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.log_json or settings.is_production:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, settings.log_level)),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Devolve um logger ligado ao modulo informado."""
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    return logger
