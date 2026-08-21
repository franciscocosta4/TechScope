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

# Patterns para tecnologias comuns extraídas via regex.
# Não dependemos de nenhuma tabela de tecnologias na base de dados.
COMMON_TECH_PATTERNS = [

    # Frontend frameworks / libraries
    r'\b(react|react\.js|reactjs)\b',
    r'\b(angular|angular\.js|angularjs)\b',
    r'\b(vue|vue\.js|vuejs)\b',
    r'\b(svelte|sveltekit)\b',
    r'\b(next\.js|nextjs)\b',
    r'\b(nuxt|nuxt\.js)\b',
    r'\b(jquery)\b',
    r'\b(bootstrap)\b',
    r'\b(tailwind|tailwindcss)\b',
    r'\b(material[\s-]?ui|mui)\b',
    r'\b(chakra[\s-]?ui)\b',

    # Backend languages
    r'\b(node\.js|nodejs)\b',
    r'\b(python)\b',
    r'\b(java)\b',
    r'\.net\b',                    
    r'\bdotnet\b',                 
    r'(?<!\w)c#(?!\w)',            
    r'\bcsharp\b',                 
    r'\basp\.net\b',               
    r'\baspnet\b',                 
    r'\bblazor\b',                 # blazor
    r'\.net[\s-]framework\b',     # .net framework
    r'\b(php)\b',
    r'\b(ruby|ruby[\s-]?on[\s-]?rails|rails)\b',
    r'\b(golang|go)\b',
    r'\b(rust)\b',
    r'\b(kotlin)\b',
    r'\b(swift)\b',
    r'\b(scala)\b',
    r'\b(perl)\b',
    r'\b(elixir)\b',
    r'\b(erlang)\b',

    # Java ecosystem
    r'\b(spring|spring[\s-]?boot|springboot)\b',
    r'\b(hibernate)\b',
    r'\b(maven)\b',
    r'\b(gradle)\b',

    # JavaScript ecosystem
    r'\b(javascript|js|es6|ecmascript)\b',
    r'\b(typescript|ts)\b',
    r'\b(express|express\.js)\b',
    r'\b(nest\.js|nestjs)\b',
    r'\b(deno)\b',
    r'\b(bun)\b',

    # Mobile
    r'\b(android)\b',
    r'\b(android[\s-]?studio)\b',
    r'\b(ios)\b',
    r'\b(flutter)\b',
    r'\b(dart)\b',
    r'\b(react[\s-]?native)\b',
    r'\b(xamarin)\b',

    # Databases SQL
    r'\b(sql)\b',
    r'\b(postgresql|postgres|psql)\b',
    r'\b(mysql|mariadb)\b',
    r'\b(sqlite)\b',
    r'\b(oracle[\s-]?db|oracle)\b',
    r'\b(sql[\s-]?server|mssql|microsoft[\s-]?sql)\b',

    # Databases NoSQL
    r'\b(mongodb|mongo)\b',
    r'\b(redis)\b',
    r'\b(cassandra)\b',
    r'\b(couchdb)\b',
    r'\b(dynamodb)\b',
    r'\b(elasticsearch|elastic[\s-]?search)\b',
    r'\b(neo4j)\b',

    # APIs / architecture
    r'\b(graphql)\b',
    r'\b(rest|restful|rest[\s-]?api)\b',
    r'\b(soap)\b',
    r'\b(websocket|websockets)\b',
    r'\b(microservices|microservices[\s-]?architecture)\b',
    r'\b(event[\s-]?driven|event[\s-]?driven[\s-]?architecture)\b',

    # Cloud providers
    r'\b(aws|amazon[\s-]?web[\s-]?services)\b',
    r'\b(azure|microsoft[\s-]?azure)\b',
    r'\b(gcp|google[\s-]?cloud|google[\s-]?cloud[\s-]?platform)\b',
    r'\b(oracle[\s-]?cloud|oci)\b',
    r'\b(alibaba[\s-]?cloud)\b',

    # Cloud services
    r'\b(lambda)\b',
    r'\b(ec2)\b',
    r'\b(s3)\b',
    r'\b(eks|ecs)\b',
    r'\b(azure[\s-]?functions)\b',

    # Containers / DevOps
    r'\b(docker)\b',
    r'\b(kubernetes|k8s)\b',
    r'\b(helm)\b',
    r'\b(terraform)\b',
    r'\b(ansible)\b',
    r'\b(puppet)\b',
    r'\b(chef)\b',

    # CI/CD
    r'\b(git)\b',
    r'\b(github)\b',
    r'\b(gitlab)\b',
    r'\b(bitbucket)\b',
    r'\b(jenkins)\b',
    r'\b(circleci)\b',
    r'\b(travis[\s-]?ci)\b',
    r'\b(github[\s-]?actions)\b',
    r'\b(azure[\s-]?devops)\b',

    # Data engineering / analytics
    r'\b(apache[\s-]?spark|spark)\b',
    r'\b(hadoop)\b',
    r'\b(kafka|apache[\s-]?kafka)\b',
    r'\b(airflow|apache[\s-]?airflow)\b',
    r'\b(databricks)\b',
    r'\b(snowflake)\b',
    r'\b(tableau)\b',
    r'\b(power[\s-]?bi|powerbi)\b',
    r'\b(qlik)\b',

    # AI / Machine Learning
    r'\b(machine[\s-]?learning|ml)\b',
    r'\b(deep[\s-]?learning)\b',
    r'\b(tensorflow)\b',
    r'\b(pytorch)\b',
    r'\b(keras)\b',
    r'\b(scikit[\s-]?learn|sklearn)\b',
    r'\b(pandas)\b',
    r'\b(numpy)\b',
    r'\b(opencv)\b',

    # Testing
    r'\b(jest)\b',
    r'\b(mocha)\b',
    r'\b(cypress)\b',
    r'\b(playwright)\b',
    r'\b(selenium)\b',
    r'\b(junit)\b',
    r'\b(pytest)\b',

    # Security
    r'\b(oauth|oauth2)\b',
    r'\b(jwt|json[\s-]?web[\s-]?token)\b',
    r'\b(ssl|tls)\b',
    r'\b(vpn)\b',
    r'\b(kali[\s-]?linux)\b',
    r'\b(owasp)\b',

    # Operating systems
    r'\b(linux)\b',
    r'\b(ubuntu)\b',
    r'\b(debian)\b',
    r'\b(centos)\b',
    r'\b(red[\s-]?hat|rhel)\b',
    r'\b(windows[\s-]?server)\b',

    # Project management / methodology
    r'\b(agile|scrum|kanban)\b',
    r'\b(jira)\b',
    r'\b(confluence)\b',
    r'\b(trello)\b',
    r'\b(asana)\b',

]


# Mapa de normalização de tecnologias.
# Agrupa variantes de escrita sob um termo canónico.
# Isto evita que .net, .net framework e asp.net apareçam como tecnologias separadas.
TECH_ALIASES: dict[str, str] = {
    # .NET ecosystem
    '.net framework': '.net',
    '.net core': '.net',
    'asp.net': '.net',
    'asp.net core': '.net',
    'aspnet': '.net',
    'dotnet': '.net',
    'c#': '.net',
    'csharp': '.net',
    'blazor': '.net',
    'entity framework': '.net',

    # JavaScript ecosystem
    'js': 'javascript',
    'ecmascript': 'javascript',
    'node.js': 'nodejs',
    'react.js': 'react',
    'vue.js': 'vue',
    'angular.js': 'angular',

    # Databases
    'postgres': 'postgresql',
    'psql': 'postgresql',
    'mongo': 'mongodb',
    'mssql': 'sql server',
    'microsoft sql': 'sql server',

    # Cloud
    'amazon web services': 'aws',
    'google cloud': 'gcp',
    'google cloud platform': 'gcp',
    'microsoft azure': 'azure',
}


def _normalize_tech_keyword(keyword: str) -> str:
    """Normaliza uma keyword de tecnologia para o seu termo canónico.

    Exemplos:
        '.net framework' → '.net'
        'node.js' → 'nodejs'
        'js' → 'javascript'
    """
    return TECH_ALIASES.get(keyword, keyword)


# Funções utilitárias de extração de keywords.
# A ordem importa: patterns mais específicos primeiro.

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
            tech = _normalize_tech_keyword(tech)
            techs_found.add(tech)

    # Tecnologias dinâmicas extraídas de keywords anteriores.
    # (opcional, se quiseres cruzar com keywords já extraídas)
    if known_technologies:
        for tech in known_technologies:
            if tech and tech.casefold() in text_lower:
                normalized = _normalize_tech_keyword(tech)
                techs_found.add(normalized)

    if techs_found:
        results['technology'] = sorted(techs_found)

    return results
