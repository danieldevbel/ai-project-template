"""Exemplo de dominio: um pipeline com etapas nomeadas e resultado auditavel.

A forma importa mais que o conteudo. Todo projeto derivado deste template
substitui as etapas por operacoes reais (extrair, transformar, inferir),
mantendo a mesma estrutura: etapas puras, resultado tipado e log por etapa.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from aiproject.logging import get_logger

T = TypeVar("T")

logger = get_logger(__name__)


class PipelineError(RuntimeError):
    """Falha em uma etapa do pipeline."""

    def __init__(self, step: str, cause: Exception) -> None:
        super().__init__(f"etapa '{step}' falhou: {cause}")
        self.step = step
        self.cause = cause


@dataclass(frozen=True, slots=True)
class StepReport:
    """Registro de execucao de uma etapa."""

    name: str
    duration_ms: float
    ok: bool


@dataclass(slots=True)
class PipelineResult(Generic[T]):
    """Saida do pipeline junto com o rastro de execucao."""

    value: T
    reports: list[StepReport] = field(default_factory=list)

    @property
    def total_ms(self) -> float:
        """Tempo total somado das etapas."""
        return sum(r.duration_ms for r in self.reports)


@dataclass(frozen=True, slots=True)
class Step(Generic[T]):
    """Uma etapa nomeada e pura do pipeline."""

    name: str
    fn: Callable[[T], T]


class Pipeline(Generic[T]):
    """Encadeia etapas, mede cada uma e falha de forma explicita."""

    def __init__(self, steps: Sequence[Step[T]]) -> None:
        if not steps:
            raise ValueError("o pipeline precisa de ao menos uma etapa")
        self._steps = list(steps)

    def run(self, value: T) -> PipelineResult[T]:
        """Executa as etapas em ordem, devolvendo valor final e relatorio."""
        result: PipelineResult[T] = PipelineResult(value=value)

        for step in self._steps:
            started = time.perf_counter()
            try:
                result.value = step.fn(result.value)
            except Exception as exc:
                elapsed = (time.perf_counter() - started) * 1000
                result.reports.append(StepReport(step.name, elapsed, ok=False))
                logger.error("step_failed", step=step.name, error=str(exc))
                raise PipelineError(step.name, exc) from exc

            elapsed = (time.perf_counter() - started) * 1000
            result.reports.append(StepReport(step.name, elapsed, ok=True))
            logger.info("step_done", step=step.name, duration_ms=round(elapsed, 2))

        return result
