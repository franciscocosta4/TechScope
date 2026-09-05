<div align="center">
  
# TechScope


A TechScope é uma ferramenta de análise do mercado tecnológico que avalia a procura por linguagens de programação, frameworks e ferramentas com base em dados reais de anúncios de emprego.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) 
</div>


## Sobre o projeto

A TechScope recolhe anúncios de emprego do **LinkedIn** e **Indeed**, analisa cada oferta e transforma-a em indicadores úteis sobre o mercado tech atual.
</br>
<strong>O LinkedIn é a principal fonte de dados</strong>, não só pela sua dimensão no mercado português mas também pela variedade de informação disponível. A plataforma combina ofertas de emprego com mais informação que o indeed, como, por exemplo, a data em que a vaga foi publicada.
Por esse motivo, o desenvolvimento e a robustez dos nossos scrapers estão especialmente focados no LinkedIn. A TechScope mantém  suporte para o Indeed, permitindo complementar os dados recolhidos e obter uma visão mais abrangente do mercado.

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

O objetivo é ajudar devs e pessoas que pretendem mudar de carreira a tomar decisões mais informadas sobre o que aprender e onde investir o seu tempo.


## Começando com o projeto

### 1. Pré-requisitos
- .NET 8.0
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
copy .env.example .env
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

Antes de executar os scrapers precisa correr: 

```bash
# instala os requirements do python para o projeto
 pip install -r requirements.txt
```

### 5. Preparar a base de dados

Na primeira execução, os scrapers criam o schema a partir de `data-pipeline/database/migrations/001_initial.sql`.

```bash
# Aplica a migration (apenas uma vez)
psql -U postgres -d techscope -f data-pipeline/database/migrations/001_initial.sql
```

### 5. Arrancar o Chrome para o Indeed

Para o scraper do Indeed, corre o ficheiro:

```bash
start_chrome_debug.bat
```

Isto abre o Chrome com o perfil do projecto e a porta de debug activa.

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
* [ ] Cálculo da quota de mercado de cada tecnologia
* [x] Análise do crescimento da procura ao longo do tempo
* [ ] Identificação automática de tendências de mercado
* [ ] Comparação entre tecnologias
* [x] Identificação de relações entre tecnologias frequentemente utilizadas em conjunto

### Aplicação Web

* [x] Frontend web
* [x] Dashboard de análise do mercado
* [x] Pesquisa e filtragem de tecnologias
* [x] Página de detalhe de tecnologia
* [x] Página de anúncios com filtros
* [ ] Comparação entre tecnologias
* [x] Tendências de mercado

### Análise Regional

* [x] Análise regional do mercado tecnológico
* [ ] Comparação da procura por tecnologia entre regiões

