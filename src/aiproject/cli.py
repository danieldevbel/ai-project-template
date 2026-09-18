"""Interface de linha de comando."""

from __future__ import annotations

import typer

from aiproject import __version__
from aiproject.logging import configure_logging, get_logger
from aiproject.pipeline import Pipeline, Step
from aiproject.settings import get_settings

app = typer.Typer(
    add_completion=False,
    help="Template de projeto de engenharia de IA.",
    no_args_is_help=True,
)


@app.command()
def version() -> None:
    """Mostra a versao instalada."""
    typer.echo(__version__)


@app.command()
def config() -> None:
    """Mostra a configuracao efetiva carregada do ambiente."""
    settings = get_settings()
    for key, value in settings.model_dump().items():
        typer.echo(f"{key} = {value}")


@app.command()
def demo(text: str = typer.Argument(..., help="Texto de entrada.")) -> None:
    """Roda um pipeline de exemplo sobre o texto informado."""
    settings = get_settings()
    configure_logging(settings)
    logger = get_logger("cli")

    pipeline: Pipeline[str] = Pipeline(
        [
            Step("normalizar", lambda s: s.strip().lower()),
            Step("remover_duplo_espaco", lambda s: " ".join(s.split())),
            Step("capitalizar", lambda s: s.capitalize()),
        ]
    )

    result = pipeline.run(text)
    logger.info("pipeline_done", steps=len(result.reports), total_ms=round(result.total_ms, 2))
    typer.echo(result.value)


if __name__ == "__main__":
    app()
