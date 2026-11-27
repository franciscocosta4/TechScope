<div align="center">
  
# TechScope


Ferramenta de análise do mercado tech que avalia a procura por linguagens de programação, frameworks e ferramentas com base em vagas publicadas online.


![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) 
![.net](https://img.shields.io/badge/.net-%23313292.svg?style=for-the-badge&logo=.net&logoColor=white) 
<br>
<a href="https://franciscocosta4.github.io/TechScope/">
Website do projeto</a>
.
<a href="https://franciscocosta4.github.io/TechScope/#manter">
Configurar e manter o projeto</a>


<img style="height:300px; width:auto;" src="web-app\wwwroot\assets\img\dashboard.jpg">
</div>

## Sobre o projeto

A TechScope recolhe anúncios de emprego do **LinkedIn**, suportando também o **Indeed**, analisa cada oferta e transforma-a em indicadores úteis sobre o mercado tech atual.
</br>
O objetivo é ajudar devs e pessoas que pretendem mudar de carreira a tomar decisões mais informadas sobre o que aprender e onde investir o seu tempo.


A aplicação permite:
- **Pesquisar por tecnologias** — pesquisa e análise individual de tecnologias presentes nos anúncios.
- **Pesquisar por Vagas** — pesquisa geral por vagas recentes, com capacidade de filtragem dos resultados.
- **Ver a procura por tecnologias** — quantos anúncios mencionam cada linguagem, framework ou ferramenta
- **Analisar tendências de crescimento** — quais tecnologias estão a subir ou a cair ao longo do tempo
- **Fazer Comparações** — compara quotas de mercado, crescimento e adoção entre tecnologias
- **Consultar Relações entre tecnologias** — identifica stacks e combinações que costumam aparecer juntas
- **Ver empresas que recrutam** — quais empresas estão a procurar perfis de determinada tecnologia
- **Normalização de tecnologias** — variantes como `.net`, `.net framework`, `asp.net` e `c#` são agrupadas sob `.net`; `node.js` → `nodejs`, `js` → `javascript`, etc.
- **Extrair informação sobre requisitos** — extrai e organiza dados como senioridade, experiência, modelo de trabalho e tecnologias mencionadas nos anúncios.
- **Integrar com o agentes de ai** — Fornecemos instruções para os agentes, permitindo ao utilizador implementar automação de maneira simples. (<a href="https://franciscocosta4.github.io/TechScope/#manter">
aprende como aqui</a>)


## Começando com o projeto

### 1. Pré-requisitos
- .NET 8.0
- Windows 10 ou 11, macOS ou Linux
- Python 3.11+ 
(beautifulsoup4
playwright
psycopg[binary]
requests
python-dotenv)

- PostgreSQL
- Google Chrome instalado (para o scraper do Indeed)

### 2. Configurar variáveis de ambiente

Cria um ficheiro `.env` na raiz do projeto. Podes copiar a partir de `.env.example`:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Os scrapers e a app lêem as seguintes variáveis do `.env`:

- `DATABASE_URL`
- `PGHOST`
- `PGPORT`
- `PGDATABASE`
- `PGUSER`
- `PGPASSWORD`

### 3. Arrancar a aplicação web

A aplicação .NET **não requer autenticação**. Basta arrancar e a dashboard abre diretamente:

```bash
cd web-app
dotnet run
```

A app fica disponível em `https://localhost:5136` (ou a porta configurada).


## Para os scrapers e base de dados: 

### 4. Instalar requirements.txt

O projeto deve usar uma **virtual environment** (venv). Isto evita conflitos com os pacotes do sistema e, no Linux/macOS, contorna o erro `externally-managed-environment` (PEP 668). A pasta `.venv/` já está no `.gitignore`.

```bash
# criar a venv (só uma vez)
python3 -m venv .venv

# ativar — Linux/macOS
source .venv/bin/activate

# ativar — Windows (PowerShell/CMD)
.venv\Scripts\activate

# instalar as dependências
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Com a venv ativa, usa `python` normalmente (`python data-pipeline/scrapers/linkedin.py`). Para sair: `deactivate`. Sem ativar, usa o caminho direto: `.venv/bin/python` (Linux/macOS) ou `.venv\Scripts\python.exe` (Windows).

> **Nota:** se `python3 -m venv` falhar com `ensurepip is not available`, instala `python3-venv` (`sudo apt install python3-venv`). Não é preciso `playwright install`: os scrapers ligam-se ao Chrome real via CDP.

### 5. Preparar a base de dados

Só precisas da base de dados `techscope` criada; não é necessária nenhuma ferramenta gráfica (DBeaver, pgAdmin, etc.). O `psql` chega:

```bash
# Só na primeira vez
psql -U postgres -c "CREATE DATABASE techscope;"

# Aplica a migration (opcional: os scrapers também o fazem automaticamente)
psql -U postgres -d techscope -f data-pipeline/database/migrations/001_initial.sql
```

### 5. Arrancar o Chrome em modo debug

O scraper do Indeed e os scrapers de keywords ligam-se a um Chrome real com a porta `9222` aberta. Os próprios scrapers já arrancam o browser automaticamente, mas podes fazê-lo manualmente:

```bash
python start_chrome_debug.py
```

Para apenas verificar se já está a correr:

```bash
python start_chrome_debug.py --check
```

O script funciona em Windows, macOS e Linux: procura o Chrome instalado (ou usa `CHROME_PATH`), abre-o com o perfil do projeto em `chrome-profile/` e espera que a porta de debug fique disponível. No Windows podes continuar a usar `start_chrome_debug.bat`, que apenas chama o script Python.

### 6. Correr os scrapers

Executa os scrapers a partir da raiz do repositório:

```bash
# Scrapers de anúncios (listings)
python data-pipeline/scrapers/indeed.py
python data-pipeline/scrapers/linkedin.py

# Scrapers de keywords (extraem descrições e analisam conteúdo)
python data-pipeline/scrapers/indeed_keywords.py
python data-pipeline/scrapers/linkedin_keywords.py
```

Cada scraper processa um batch de até 150 jobs por execução. Corre-os várias vezes até não haver mais jobs para processar.

> **Nota:** Os scrapers de keywords do LinkedIn precisam do Chrome debug aberto porque o LinkedIn carrega as descrições via JavaScript.

## Roadmap

- [x] Scrapers para LinkedIn e Indeed
- [x] Estrutura inicial da base de dados
- [x] Persistência em PostgreSQL
- [x] Dashboard web com pesquisa de tecnologias
- [x] Extração de keywords de descrições (seniority, experiência, modelo de trabalho, tecnologias)

### Análise do Mercado

* [x] Pesquisa e análise individual de tecnologias
* [x] Contagem de anúncios por tecnologia
* [x] Cálculo da quota de mercado de cada tecnologia
* [x] Análise do crescimento da procura ao longo do tempo
* [ ] Comparação entre tecnologias
* [x] Identificação de relações entre tecnologias frequentemente utilizadas em conjunto

### Aplicação Web

* [x] Frontend web
* [x] Dashboard de análise do mercado
* [x] Pesquisa e filtragem de tecnologias
* [x] Página de detalhe de tecnologia
* [x] Página de anúncios com filtros
* [x] Tendências de mercado

### Análise Regional

* [x] Análise regional do mercado tecnológico

