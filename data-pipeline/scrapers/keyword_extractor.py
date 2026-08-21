"""Extração de keywords de descrições de anúncios de emprego."""

from __future__ import annotations

import re
from typing import Any

# Patterns regex por categoria.
# A ordem importa: patterns mais específicos primeiro.

SENIORITY_PATTERNS = [
    (r'\b(senior|sênior|seniority|sr\.)\b', 'senior'),
    (r'\b(lead|staff|principal|especialista|expert)\b', 'senior'),
    (r'\b(mid[\s-]level|intermediate|pleno|pleno[\s-]level)\b', 'mid'),
    (r'\b(junior|júnior|entry[\s-]level|estágio|estagiário|trainee|jr\.)\b', 'junior'),
]

EXPERIENCE_PATTERNS = [
    (r'\b(\d+)\+?\s*(?:anos?|years?)[\s\-+]*de[\s\-+]*(?:experiência|experience)?\b', 'years'),
    (r'\b(\d+)\+?\s*(?:anos?|years?)[\s\-+]*(?:de[\s\-+]*(?:experiência|experience))?\b', 'years'),
]

WORK_MODEL_PATTERNS = [
    (r'\b(remoto|remote|wfh|work[\s-]from[\s-]home|trabalho[\s-]remoto)\b', 'remote'),
    (r'\b(híbrido|hybrid|hibrído|híbrida|hybrida)\b', 'hybrid'),
    (r'\b(on[\s-]site|presencial|office|no[\s-]escritório)\b', 'onsite'),
]

# Patterns para tecnologias comuns que não dependem da tabela Technologies.
COMMON_TECH_PATTERNS = [
    r'\b(react|react\.js|reactjs)\b',
    r'\b(angular|angular\.js|angularjs)\b',
    r'\b(vue|vue\.js|vuejs)\b',
    r'\b(node\.js|nodejs)\b',
    r'\b(python)\b',
    r'\b(java)\b',
    r'\b(csharp|c#)\b',
    r'\b(\.net|dotnet)\b',
    r'\b(php)\b',
    r'\b(ruby)\b',
    r'\b(golang|go)\b',
    r'\b(rust)\b',
    r'\b(kotlin)\b',
    r'\b(swift)\b',
    r'\b(docker)\b',
    r'\b(kubernetes|k8s)\b',
    r'\b(aws|amazon[\s-]web[\s-]services)\b',
    r'\b(azure|microsoft[\s-]azure)\b',
    r'\b(gcp|google[\s-]cloud)\b',
    r'\b(terraform)\b',
    r'\b(typescript)\b',
    r'\b(javascript)\b',
    r'\b(sql)\b',
    r'\b(postgresql|postgres)\b',
    r'\b(mysql|mariadb)\b',
    r'\b(mongodb|mongo)\b',
    r'\b(redis)\b',
    r'\b(graphql)\b',
    r'\b(rest|restful)\b',
    r'\b(git)\b',
    r'\b(agile|scrum)\b',
    r'\b(jira)\b',
]


def _match_patterns(text: str, patterns: list[tuple[str, str]]) -> set[str]:
    """Aplica uma lista de patterns regex e retorna as categorias encontradas."""
    found: set[str] = set()
    text_lower = text.casefold()
    for pattern, category in patterns:
        if re.search(pattern, text_lower):
            found.add(category)
    return found


def _extract_experience_years(text: str) -> set[str]:
    """Extrai expressões de anos de experiência do texto."""
    found: set[str] = set()
    text_lower = text.casefold()
    for pattern, _ in EXPERIENCE_PATTERNS:
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            years = match.group(1)
            found.add(f"{years}+ anos")
    return found


def extract_keywords(
    title: str | None,
    description: str | None,
    known_technologies: list[str] | None = None,
) -> dict[str, list[str]]:
    """Extrai keywords categorizadas de título e descrição.

    Args:
        title: Título do anúncio.
        description: Texto completo da descrição.
        known_technologies: Lista de tecnologias conhecidas (da tabela Technologies)
            para matching dinâmico.

    Returns:
        Dicionário {categoria: [keywords]}.
        Categorias possíveis: seniority, experience, work_model, technology.
    """
    text = " ".join(filter(None, [title, description]))
    if not text:
        return {}

    results: dict[str, list[str]] = {}

    # Seniority
    seniority = _match_patterns(text, SENIORITY_PATTERNS)
    if seniority:
        results['seniority'] = sorted(seniority)

    # Experiência em anos
    experience = _extract_experience_years(text)
    if experience:
        results['experience'] = sorted(experience)

    # Modelo de trabalho
    work_model = _match_patterns(text, WORK_MODEL_PATTERNS)
    if work_model:
        results['work_model'] = sorted(work_model)

    # Tecnologias
    techs_found: set[str] = set()
    text_lower = text.casefold()

    # Patterns comuns
    for pattern in COMMON_TECH_PATTERNS:
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            tech = match.group(0)
            techs_found.add(tech)

    # Tecnologias dinâmicas da BD (normalizadas para lowercase)
    if known_technologies:
        for tech in known_technologies:
            if tech and tech.casefold() in text_lower:
                techs_found.add(tech)

    if techs_found:
        results['technology'] = sorted(techs_found)

    return results
