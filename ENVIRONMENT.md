
# Por que não temos autenticação

A aplicação **não tem login, registo nem qualquer sistema de autenticação**. Esta decisão foi tomada porque:

1. **Não há personalização por utilizador** — a app mostra dados agregados do mercado (total de anúncios, tecnologias mais procuradas, tendências). Não há filtros guardados, preferências ou dados privados.
2. **É uma aplicação pública de leitura** — todas as rotas são `GET`. Os scrapers é que escrevem na base de dados; a web app só lê.
3. **Sem complicações de manutenção** — não há Identity, JWT, cookies, sessões, passwords nem multi-tenancy.
4. **Demo pública simples** — qualquer pessoa pode entrar na app e ver o dashboard. Sem barreiras.

Isto também simplifica o deployment: não precisamos de HTTPS obrigatório por causa de cookies, nem de gestão de segredos de auth.

---

## Arquitetura da web app 

### Dashboard

- total de anúncios
- tecnologias mais procuradas
- gráfico de tendências do mercado
- distribuição regional
- volume de anúncios recentes
- pesquisa rápida de tecnologias que leva para a página de detalhe da tecnologia

### Página de detalhe da tecnologia

- nome da tecnologia
- número de anúncios
- tendência mensal
- salários
- tecnologias relacionadas
- empresas que recrutam
- anúncios recentes relacionados

### Página de anúncios

- barra de pesquisa para anúncios
- filtros
- cartões de anúncio por ordem, do mais recente para o mais antigo
- paginação
- opção de abrir o link original do anúncio

## Modelo da Base de Dados gerada na pipeline

```mermaid
erDiagram

    Companies ||--o{ Jobs : publica

    Jobs ||--o{ JobTechnologies : contém

    Technologies ||--o{ JobTechnologies : aparece_em


    Companies {
        uuid Id PK
        string Name
        string Website
        string Location
        datetime CreatedAt
    }


    Jobs {
        uuid Id PK
        uuid CompanyId FK
        string Title
        string Location
        decimal SalaryMin
        decimal SalaryMax
        text Description
        string Source
        string ExternalId
        date DatePosted
        datetime CreatedAt
    }


    Technologies {
        bigint Id PK
        string Name
        string Category
        datetime CreatedAt
    }


    JobTechnologies {
        uuid JobId FK
        bigint TechnologyId FK
        decimal ConfidenceScore
    }
```

---
# Ligação à base de dados

A ligação ao PostgreSQL foi centralizada em `data-pipeline/database/postgres.py` para evitar repetir configuração nos scrapers.
Assim, a configuração fica num único sítio e é mais fácil de manter.

# Como evitamos empresas duplicadas

A tabela `companies` tem `UNIQUE(name)` porque o mesmo nome deve representar a mesma empresa ao longo da pipeline.
Antes de guardar um job, o script confirma se a empresa já existe e reutiliza o `company_id` dessa linha.
Se não existir, a empresa é criada primeiro.

# Fluxo para gravar uma empresa e um job

Primeiro o script garante que a empresa existe na tabela `companies`.
Se a empresa ainda não existir, ela é criada e o código recebe o `company_id` dessa linha.
Depois o script procura um job com a mesma combinação de `company_id`, `title` e `location`.
Se encontrar, não grava outro igual.
Se não encontrar, cria o job novo ligado à empresa certa.

Isto evita duplicados simples e mantém a relação entre empresas e anúncios limpa.

# O que é o `external_id`

O `external_id` usa o link do anúncio quando existe.
Quando não existe um identificador estável, é gerado um hash com campos como título, empresa, localização e source para manter consistência.

# Porque existem as tabelas `companies` e `jobs`

A tabela `companies` existe para normalizar empresas e evitar duplicados.
A tabela `jobs` guarda o anúncio principal para depois servir análises na app .NET.

`date_posted` fica como `DATE` e não `TIMESTAMPTZ`, porque nos scrapers o que normalmente vem do LinkedIn/Indeed é só a data do anúncio e não uma hora exata.
O `created_at` continua como `TIMESTAMPTZ` porque aí sim interessa saber o momento exacto em que o registo entrou na base de dados.

# Porque a pipeline está separada do backend .NET

A separação em `data-pipeline/scrapers` e `data-pipeline/database` foi feita para manter a pipeline Python isolada do backend .NET.
Isso facilita manutenção, organização e crescimento futuro do projeto.

# Onde fica o schema da base de dados

O schema fica em `data-pipeline/database/migrations/001_initial.sql` porque a criação da estrutura da base deve viver ao lado da lógica de persistência e da pipeline que a usa.

# Como ligamos jobs a tecnologias

Cada scraper tem duas variáveis importantes: `QUERY` e `TECHNOLOGY_NAME`.
`QUERY` é o termo usado no site para fazer a pesquisa.
`TECHNOLOGY_NAME` é o nome que guardamos na tabela `technologies`.

Por exemplo, se quisermos analisar `.NET`, podemos usar `QUERY=".net"` e `TECHNOLOGY_NAME=".NET"`.
Se o título ou a descrição mencionar claramente a tecnologia, o score vai para `1.0`.
Se a query for exactamente a tecnologia, o score fica em `0.9`.
Se a relação vier apenas do contexto da pesquisa, o score fica em `0.7`.

A tabela `technologies` usa um ID simples auto-incrementado porque facilita leitura e manutenção.
A relação final é guardada em `job_technologies` com `confidence_score`.

# Como funciona a paginação guardada

Para não começar sempre no `0`, a pipeline guarda o último `start` usado num ficheiro CSV local: `data-pipeline/scrapers/scraper_state.csv`.
Cada linha associa `source` + `query` ao último bloco percorrido.

Na execução seguinte, o scraper lê esse ficheiro e retoma a partir de `last_start + PAGE_SIZE`.
Se a `QUERY` mudar, a chave muda também e a paginação volta automaticamente a `0`.

Isto mantém a lógica simples e evita repetir sempre as mesmas páginas quando o script é corrido várias vezes seguidas.

# Como reduzimos rate limiting e verificações

   ## LinkedIn

   No LinkedIn tentamos reduzir bloqueios sem forçar demasiado o site:

   - usamos `headers` mais completos, em vez de um pedido mínimo
   - incluímos `User-Agent`, `Accept`, `Accept-Language` e `Referer`
   - fazemos uma pausa aleatória antes de cada pedido
   - evitamos correr muitas páginas seguidas sem necessidade

   ## Indeed

   No Indeed o problema é mais agressivo, porque pode surgir verificação logo no início.

   Para reduzir isso:

   - abrimos o browser de forma visível (`headless=False`)
   - usamos um perfil persistente para reutilizar cookies e sessão
   - ligamos ao Chrome real via `remote debugging`
   - mantemos pausas aleatórias entre acções
   - não insistimos quando aparece verificação; o scraper deve parar e deixar o utilizador intervir

   O uso do perfil persistente e do Chrome real ajuda porque o site vê um ambiente mais estável, com histórico e sessão reutilizável, em vez de uma instância nova a cada execução.

# Chrome real para o Indeed

O scraper do Indeed pode ligar-se a um Chrome real via `remote debugging` para reutilizar cookies e sessão do teu PC.
Para isso existe o ficheiro `start_chrome_debug.bat`, que abre o Chrome com a porta `9222` activa.

O perfil usado por esse browser fica em `data-pipeline/scrapers/chrome-profile/` e é criado automaticamente quando corres o Chrome desse modo ou quando o scraper o usa pela primeira vez.


# Links base para testar

Indeed:
`https://pt.indeed.com/jobs?q=python&l=Porto&radius=50&start=0`

LinkedIn:
`https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=javascript&location=Portugal&start=120`

## Filtros úteis

| Filtro           | LinkedIn / Google Jobs | Indeed            |
|------------------|------------------------|-------------------|
| Últimas 24h      | `f_TPR=r86400`         | `fromage=1`       |
| Última semana    | `f_TPR=r604800`        | `fromage=7`       |
| Full-time        | `f_JT=F`               | `jt=fulltime`     |
| Remote           | `f_WT=2`               | `remotejob=1`     |
| Júnior / Entry   | `f_E=2`                | `explvl=entry_level` |


# Por que mudámos para PascalCase

O schema original usava `snake_case` (`id`, `created_at`, `company_id`). Mudámos tudo para **PascalCase** (`"Id"`, `"CreatedAt"`, `"CompanyId"`) por três razões:

1. **Alinhamento com o .NET** – as propriedades das entidades no C# seguem PascalCase (`Id`, `CreatedAt`, `CompanyId`). Manter os mesmos nomes no PostgreSQL evita mapeamentos manuais ou atributos `[Column("created_at")]` em todo o lado.
2. **Consistência interna** – ao usar aspas duplas nas definições SQL (`"Id"`, `"CreatedAt"`), o PostgreSQL preserva a capitalização exacta, tornando o schema auto-documentado e igual ao modelo de domínio.
3. **Menos atrito em ferramentas** – ORMs (EF Core, Dapper com mapeamento automático) funcionam *out-of-the-box* quando os nomes coincidem.


### Migrações .NET vs Migrações Python

- As migrações do pipeline Python (`data-pipeline/database/migrations/`) são responsáveis por criar e manter o schema base (`Companies`, `Jobs`, `Technologies`, `JobTechnologies`). Este schema é partilhado entre a pipeline Python e a aplicação .NET.
- As migrações da aplicação .NET (caso utilizem EF Core ou similar) ficam em pasta própria (ex.: `backend/migrations/` ou definida no projeto .NET) e são responsáveis apenas por alterações no modelo da aplicação, não tocando nas tabelas base criadas pela pipeline Python.

