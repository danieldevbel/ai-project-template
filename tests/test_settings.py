"""Testes da configuracao."""

from __future__ import annotations

from aiproject.settings import Settings


def test_valores_padrao():
    settings = Settings(_env_file=None)
    assert settings.environment == "dev"
    assert settings.random_seed == 42
    assert settings.is_production is False


def test_le_do_ambiente(monkeypatch):
    monkeypatch.setenv("APP_ENVIRONMENT", "prod")
    monkeypatch.setenv("APP_LOG_LEVEL", "ERROR")
    settings = Settings(_env_file=None)
    assert settings.is_production is True
    assert settings.log_level == "ERROR"


def test_valor_invalido_falha(monkeypatch):
    import pytest
    from pydantic import ValidationError

    monkeypatch.setenv("APP_ENVIRONMENT", "producao")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
