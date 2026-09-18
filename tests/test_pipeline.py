"""Testes do pipeline de exemplo."""

from __future__ import annotations

import pytest

from aiproject.pipeline import Pipeline, PipelineError, Step


def test_executa_etapas_em_ordem():
    pipeline = Pipeline([Step("dobrar", lambda x: x * 2), Step("somar", lambda x: x + 1)])
    result = pipeline.run(3)
    assert result.value == 7
    assert [r.name for r in result.reports] == ["dobrar", "somar"]
    assert all(r.ok for r in result.reports)


def test_pipeline_vazio_e_rejeitado():
    with pytest.raises(ValueError, match="ao menos uma etapa"):
        Pipeline([])


def test_falha_identifica_a_etapa():
    def explode(_: int) -> int:
        raise ZeroDivisionError("boom")

    pipeline = Pipeline([Step("ok", lambda x: x), Step("ruim", explode)])

    with pytest.raises(PipelineError) as exc:
        pipeline.run(1)

    assert exc.value.step == "ruim"
    assert isinstance(exc.value.cause, ZeroDivisionError)


def test_relatorio_registra_etapa_que_falhou():
    pipeline = Pipeline([Step("ruim", lambda _: 1 / 0)])
    with pytest.raises(PipelineError):
        pipeline.run(1)


def test_total_ms_soma_as_etapas():
    pipeline = Pipeline([Step("a", lambda x: x), Step("b", lambda x: x)])
    result = pipeline.run(0)
    assert result.total_ms == pytest.approx(sum(r.duration_ms for r in result.reports))
