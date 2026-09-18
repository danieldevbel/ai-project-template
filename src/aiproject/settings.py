"""Configuracao da aplicacao.

Toda configuracao vem de variaveis de ambiente ou de um arquivo `.env`, nunca
de constantes espalhadas pelo codigo. Isso mantem o mesmo binario valido em
desenvolvimento, homologacao e producao.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


class Settings(BaseSettings):
    """Configuracao tipada e validada na inicializacao."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
    )

    app_name: str = Field(default="ai-project-template", description="Nome do servico.")
    environment: Literal["dev", "staging", "prod"] = Field(default="dev")
    log_level: LogLevel = Field(default="INFO")
    log_json: bool = Field(default=False, description="Emite log estruturado em JSON.")
    data_dir: Path = Field(default=Path("data"), description="Raiz dos dados locais.")
    random_seed: int = Field(default=42, ge=0, description="Semente de reprodutibilidade.")

    @property
    def is_production(self) -> bool:
        """Indica se o processo roda em producao."""
        return self.environment == "prod"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Devolve a configuracao carregada uma unica vez por processo."""
    return Settings()
