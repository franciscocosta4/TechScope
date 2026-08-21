"""Estado simples para retoma de scraping entre execuções."""

from __future__ import annotations

import csv
from pathlib import Path

STATE_PATH = Path(__file__).resolve().parent / "scraper_state.csv"


def _load_state() -> dict[str, str]:
    """Carrega o estado do CSV como dicionário."""
    if not STATE_PATH.exists():
        return {}

    state: dict[str, str] = {}
    with STATE_PATH.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            source = (row.get("source") or "").strip()
            query = (row.get("query") or "").strip()
            last_start = (row.get("last_start") or "").strip()

            if not source or not query:
                continue

            try:
                state[f"{source}:{query.casefold()}"] = last_start
            except ValueError:
                continue

    return state


def _save_state(state: dict[str, str]) -> None:
    """Guarda o estado no CSV."""
    with STATE_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["source", "query", "last_start"])
        for key, last_start in state.items():
            parts = key.split(":", 1)
            if len(parts) == 2:
                source, query = parts
                writer.writerow([source, query, last_start])


def get_next_start(source: str, query: str, page_size: int, default_start: int = 0) -> int:
    """Retoma paginação por offset."""
    key = f"{source}:{query.strip().casefold()}"
    state = _load_state()
    last_start = state.get(key)

    if last_start:
        try:
            return int(last_start) + page_size
        except ValueError:
            pass

    return default_start


def update_last_start(source: str, query: str, last_start: int) -> None:
    """Guarda última paginação por offset."""
    key = f"{source}:{query.strip().casefold()}"
    state = _load_state()
    state[key] = str(last_start)
    _save_state(state)
