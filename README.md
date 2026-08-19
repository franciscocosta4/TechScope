<div align="center">
  
# TechScope


A TechScope é uma ferramenta de análise do mercado tecnológico que avalia a procura por linguagens de programação, frameworks e ferramentas com base em dados reais de anúncios de emprego.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) 
</div>


## Sobre o projeto

A TechScope recolhe anúncios de emprego do **LinkedIn** e **Indeed**, analisa cada oferta e transforma-a em indicadores úteis sobre o mercado tech atual.

A aplicação mostra:

- **Procura por tecnologia** — quantos anúncios mencionam cada linguagem, framework ou ferramenta
- **Tendências de crescimento** — quais tecnologias estão a subir ou a cair ao longo do tempo
- **Comparações** — compara quotas de mercado, crescimento e adoção entre tecnologias
- **Relações entre tecnologias** — identifica stacks e combinações que costumam aparecer juntas
- **Informação salarial** — quando disponível nos anúncios
- **Empresas que recrutam** — quais empresas estão a procurar perfis de determinada tecnologia

O objetivo é ajudar devs e pessoas que pretendem mudar de carreira a tomar decisões mais informadas sobre o que aprender e onde investir o seu tempo.

# Arquitetura

O sistema está dividido em três componentes principais:

```mermaid
flowchart TD

    Sources[(Fontes de Emprego)]

    subgraph PythonPipeline[Python Pipeline]
        Scheduler[Agendador Diário]
        Scrapers[Scrapers de Emprego]
        Processor[Processamento de Dados]
    end

    DB[(PostgreSQL)]

    subgraph NETApp[.NET Application]
        API[ASP.NET Core API]
        Analytics[Motor de Análise]
    end

    Frontend[Dashboard Web]

    Sources --> Scheduler
    Scheduler --> Scrapers
    Scrapers --> Processor
    Processor --> DB


    DB --> API
    API --> Analytics
    Analytics --> Frontend
```

## Funcionalidades Principais

### Análise de Tecnologias

Pesquisa por tecnologias:

Exemplos:
* Java
* React
* Node.js
* Docker
* Kubernetes

Devolve:
* Número de anúncios disponíveis
* Quota de mercado
* Crescimento ao longo do tempo



### Comparação de Tecnologias

Exemplo de Comparação:

| Métrica | Spring Boot | Node.js |
| --- | --- | --- |
| Número de anúncios | 1000 | 250 |
| Crescimento | +10% | -2% |
| Competências relacionadas |  |  |


### Tendências de Mercado

Identifica tecnologias com procura crescente.

Exemplo:

```
Tecnologia     Crescimento

Kubernetes     +35%
Docker         +28%
React          +15%
```



## Começando com o projeto

### 1. Pré-requisitos

- Python 3.11+
- PostgreSQL
- Google Chrome instalado (para o scraper do Indeed)

### 2. Criar e activar o ambiente virtual

Na raiz do projecto:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Cria um ficheiro `.env` na raiz do projecto. Podes copiar a partir de `.env.example`:

```bash
copy .env.example .env
```

Os scrapers em Python lêem as seguintes variáveis do `.env`:

- `DATABASE_URL`
- `PGHOST`
- `PGPORT`
- `PGDATABASE`
- `PGUSER`
- `PGPASSWORD`

### 5. Arrancar o Chrome para o Indeed

Para o scraper do Indeed, corre o ficheiro:

```bash
start_chrome_debug.bat
```

Isto abre o Chrome com o perfil do projecto e a porta de debug activa.

### 6. Correr os scrapers

Na primeira execução, os scrapers criam o schema base a partir de `data-pipeline/database/migrations/001_initial.sql`.

Executa os scrapers a partir da raiz do repositório:

```bash
python data-pipeline/scrapers/indeed.py
python data-pipeline/scrapers/linkedin.py
```


## Roadmap

- [x] Scrapers para linkedin e indeed
- [x] Estrutura inicial da base de dados
- [x] Persistência em PostgreSQL

### Análise do Mercado

* [ ] Pesquisa e análise individual de tecnologias
* [ ] Contagem de anúncios por tecnologia
* [ ] Cálculo da quota de mercado de cada tecnologia
* [ ] Análise do crescimento da procura ao longo do tempo
* [ ] Identificação automática de tendências de mercado
* [ ] Comparação entre tecnologias
* [ ] Identificação de relações entre tecnologias frequentemente utilizadas em conjunto
* [ ] Recolha e apresentação de informação salarial quando disponível

### Aplicação Web

* [ ] Frontend web
* [ ] Dashboard de análise do mercado
* [ ] Pesquisa e filtragem de tecnologias

### Análise Regional

* [ ] Análise regional do mercado tecnológico
* [ ] Comparação da procura por tecnologia entre regiões

