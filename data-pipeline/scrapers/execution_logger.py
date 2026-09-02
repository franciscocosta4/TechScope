"""execution_logger.py

Módulo de logging de execuções dos scrapers.

Cria/atualiza um único ficheiro JSON (execution.json) com a estrutura pedida:

{
    "l": {                     # LinkedIn
        "last_run": "2026-09-01T08:31:42Z",
        "status": "success",
        "rodarscraper1": "success",   ← linkedin.py
        "rodarscraper2": "success"    ← linkedin_keywords.py
    },
    "i": {                     # Indeed
        "last_run": "2026-09-01T08:32:05Z",
        "status": "success",
        "rodarscraper1": "success",   ← indeed.py
        "rodarscraper2": "success"    ← indeed_keywords.py
    }
}
"""

import json
import os
from datetime import datetime
from pathlib import Path

# ----------------------------------------------------------------------
# Configurações
# ----------------------------------------------------------------------
EXECUTION_JSON_PATH = Path("execution.json")   # pode ser caminho absoluto se desejar


def _utc_iso_now() -> str:
    """Timestamp UTC no formato ISO‑8601 (ex.: 2026-09-01T08:31:42Z)."""
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _load_execution_json() -> dict:
    """Carrega o ficheiro JSON existente ou devolve dicionário vazio."""
    if not EXECUTION_JSON_PATH.is_file():
        return {"l": {}, "i": {}}
    try:
        with open(EXECUTION_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # ficheiro corrompido ou inexistente → recomeça do zero
        return {"l": {}, "i": {}}


def _write_execution_json_atomically(data: dict) -> None:
    """Escreve o dicionário inteiro de forma atómica (temp file → replace)."""
    tmp_path = EXECUTION_JSON_PATH.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(tmp_path, EXECUTION_JSON_PATH)   # operação atómica


# ----------------------------------------------------------------------
# Funções internas genéricas
# ----------------------------------------------------------------------
def _write_scraper_status(
    target: str,
    scraper_key: str,
    success: bool,
    *,
    run_timestamp: str | None = None,
) -> None:
    """
    Actualiza um bloco específico (LinkedIn 'l' ou Indeed 'i') no ficheiro
    execution.json, registando apenas o estado do scraper indicado.

    Parameters
    ----------
    target : str                → "l" (LinkedIn) ou "i" (Indeed)
    scraper_key : str           → "rodarscraper1" ou "rodarscraper2"
    success : bool              → True ⇒ sucesso, False ⇒ erro
    run_timestamp : str | None  → ISO‑8601 UTC opcional
    """
    data = _load_execution_json()

    # Garante que o bloco alvo existe
    block = data.setdefault(target, {})

    timestamp = run_timestamp or _utc_iso_now()
    result = "success" if success else "error"

    block.update(
        {
            "last_run": timestamp,
            "status": result,
            scraper_key: result,
        }
    )

    _write_execution_json_atomically(data)


# ----------------------------------------------------------------------
# Funções públicas — LinkedIn
# ----------------------------------------------------------------------
def write_linkedin_scraper1_status(success: bool, *, run_timestamp: str | None = None) -> None:
    """Regista o estado de linkedin.py (scraper 1) na chave 'l'."""
    _write_scraper_status("l", "rodarscraper1", success, run_timestamp=run_timestamp)


def write_linkedin_scraper2_status(success: bool, *, run_timestamp: str | None = None) -> None:
    """Regista o estado de linkedin_keywords.py (scraper 2) na chave 'l'."""
    _write_scraper_status("l", "rodarscraper2", success, run_timestamp=run_timestamp)


# ----------------------------------------------------------------------
# Funções públicas — Indeed
# ----------------------------------------------------------------------
def write_indeed_scraper1_status(success: bool, *, run_timestamp: str | None = None) -> None:
    """Regista o estado de indeed.py (scraper 1) na chave 'i'."""
    _write_scraper_status("i", "rodarscraper1", success, run_timestamp=run_timestamp)


def write_indeed_scraper2_status(success: bool, *, run_timestamp: str | None = None) -> None:
    """Regista o estado de indeed_keywords.py (scraper 2) na chave 'i'."""
    _write_scraper_status("i", "rodarscraper2", success, run_timestamp=run_timestamp)
