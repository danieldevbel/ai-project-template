# ai-project-template

Template de referência para projetos de engenharia de IA em Python. Define a estrutura, a configuração, o logging, os testes e o CI que os demais projetos herdam, para que todo repositório novo comece já em nível de produção.

*Reference template for Python AI engineering projects: structure, configuration, structured logging, tests and CI, so every new repository starts production-ready.*

![ci](https://github.com/danieldevbel/ai-project-template/actions/workflows/ci.yml/badge.svg)
![python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)
![license](https://img.shields.io/badge/license-MIT-green)

---

## Problema

Projetos de IA costumam nascer como notebook e morrer como notebook. Quando chega a hora de colocar em produção, faltam as mesmas coisas: configuração fora do código, log que dá para investigar, teste que pega regressão, fronteira clara entre domínio e infraestrutura. Refazer essa base a cada projeto custa dias e o resultado sai diferente toda vez.

Este template resolve isso uma única vez.

## O que ele entrega

| Camada | Escolha | Por quê |
|---|---|---|
| Dependências | `uv` + `pyproject.toml` | Resolução em segundos, lockfile reprodutível |
| Configuração | `pydantic-settings` | Configuração tipada e validada na inicialização, não no meio da execução |
| Logging | `structlog` | Legível em dev, JSON em produção, sem mudar código |
| CLI | `typer` | Toda funcionalidade acessível por comando, não só por import |
| Qualidade | `ruff` + `mypy --strict` | Lint, formatação e tipos como porta de entrada |
| Testes | `pytest` + cobertura | Falha de etapa identificada pelo nome |
| CI | GitHub Actions | Matriz 3.11 e 3.12, mesmo comando que roda local |

## Arquitetura

```
src/aiproject/
  settings.py    configuração tipada, carregada uma vez por processo
  logging.py     logging estruturado, formato definido pelo ambiente
  pipeline.py    domínio: etapas nomeadas, resultado auditável
  cli.py         interface de linha de comando
tests/           espelha src/, um arquivo por módulo
```

A regra que sustenta o template: **o domínio não conhece a infraestrutura**. `pipeline.py` não sabe de onde vem a configuração nem para onde vai o log. Isso mantém o núcleo testável sem mock e permite trocar o entorno sem tocar na lógica.

O `Pipeline` mede cada etapa e, na falha, diz qual etapa quebrou e por quê:

```python
from aiproject.pipeline import Pipeline, Step

pipeline = Pipeline([
    Step("normalizar", lambda s: s.strip().lower()),
    Step("capitalizar", lambda s: s.capitalize()),
])

result = pipeline.run("  TEXTO  BRUTO ")
result.value          # "Texto  bruto"
result.total_ms       # tempo somado das etapas
result.reports        # [StepReport(name=..., duration_ms=..., ok=True), ...]
```

## Como rodar

```bash
git clone https://github.com/danieldevbel/ai-project-template.git
cd ai-project-template
make install
make check
```

`make check` roda exatamente o que o CI roda: lint, formatação, tipos e testes.

```bash
uv run aiproject demo "  TEXTO   BRUTO "
uv run aiproject config
```

## Como derivar um projeto novo

1. Use este repositório como *template* no GitHub (botão **Use this template**).
2. Renomeie `src/aiproject/` para o pacote do projeto e ajuste `pyproject.toml` (`name`, `description`, `packages`, `scripts`).
3. Substitua `pipeline.py` pelo domínio real e apague o teste de exemplo.
4. Ajuste o prefixo de ambiente em `settings.py` (`env_prefix`).
5. Rode `make check` antes do primeiro commit.

## Decisões e alternativas descartadas

- **`uv` em vez de Poetry**: instalação de ordem de magnitude mais rápida no CI, com o mesmo lockfile reprodutível. Poetry continua válido; a troca é de uma linha no `Makefile`.
- **`structlog` em vez de `logging` puro**: log estruturado é o que torna a investigação em produção viável. Com `logging` puro, chega-se à mesma coisa reescrevendo formatadores à mão.
- **`mypy --strict` desde o início**: relaxar depois é barato, apertar depois em base grande é caro.
- **Sem `src/` implícito**: o layout `src/` evita que o teste importe o pacote do diretório de trabalho em vez do instalado, que é a origem clássica de "passa local e falha no CI".

## Limitações conhecidas

- Não inclui camada de API. Há um extra opcional (`pip install '.[api]'`) com FastAPI, mas nenhuma rota é fornecida, porque o contrato de API é específico de cada projeto.
- Não inclui Dockerfile. Projetos derivados que precisam de contêiner adicionam o seu, já que a imagem base depende de haver GPU, driver ou dependência de sistema.
- Não inclui rastreamento de experimentos (MLflow ou equivalente). É dependência pesada e só faz sentido em projetos que de fato treinam modelo.
- A cobertura de testes cobre o domínio, não o CLI. O CLI é fino de propósito, para que isso seja aceitável.

## Licença

MIT. Ver [LICENSE](LICENSE).
