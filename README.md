<div align="center">
  
# TechScope


O TechScope é uma aplicação web de análise do mercado tecnológico que avalia a procura por linguagens de programação, frameworks e ferramentas com base em dados reais de anúncios de emprego.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) 
</div>


## Sobre o projeto

O sistema recolhe ofertas de emprego do Linkedin e do Indeed, analisa cada anúncio e transforma essa informação em insights úteis sobre o mercado tech atual. 
A app fornece informação sobre procura de tecnologias, tendências de crescimento do mercado, comparações entre tecnologias, informação salarial quando disponível e relações entre tecnologias que costumam ser usadas em conjunto.
O objectivo da TechScope é ajudar devs a melhor compreenderem os requisitos do mercado e identificarem oportunidades de crescimento profissional.

# Arquitetura

O sistema está dividido em três componentes principais:

- **Pipeline de Dados em Python**
  - Recolha de anúncios de emprego
  - Processamento de dados
  - Extração de tecnologias
  - Normalização de dados

- **Base de Dados PostgreSQL**
  - Guarda anúncios de emprego
  - Guarda empresas
  - Guarda tecnologias
  - Guarda relações entre anúncios e tecnologias

- **WEB APP .NET**
  - Mostra os dados e análises
  - Gere a experiência de utilização
  - Consome a API para obter insights



## Começando com o projecto

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


## Roadmap

- [x] Scrapers para linkedin e indeed
- [x] Estrutura inicial da base de dados
- [ ] Web App .NET
- [ ] Frontend web
- [ ] Dashboards em tempo real
- [ ] Extração de tecnologias com machine learning
- [ ] Previsão salarial
- [ ] Análise regional do mercado
- [ ] Motor de recomendação de empregos
- [ ] Previsão histórica do mercado
