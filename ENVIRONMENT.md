
## Arquitectura do Sistema

```mermaid
flowchart TD

    Sources[(Fontes de Emprego)]

    subgraph PythonPipeline[Python Pipeline]
        Scheduler[Agendador Diário]
        Scrapers[Scrapers de Emprego]
        Processor[Processamento de Dados]
        NLP[Extração de Tecnologias]
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
    Processor --> NLP
    NLP --> DB

    DB --> API
    API --> Analytics
    Analytics --> Frontend
```

## Modelo da Base de Dados

```mermaid
erDiagram

    COMPANIES ||--o{ JOBS : publica

    JOBS ||--o{ JOB_TECHNOLOGIES : contém

    TECHNOLOGIES ||--o{ JOB_TECHNOLOGIES : aparece_em


    COMPANIES {
        uuid id PK
        string name
        string website
        string location
        datetime created_at
    }


    JOBS {
        uuid id PK
        uuid company_id FK
        string title
        string location
        decimal salary_min
        decimal salary_max
        text description
        string source
        string external_id
        date date_posted
        datetime created_at
    }


    TECHNOLOGIES {
        bigint id PK
        string name
        string category
        datetime created_at
    }


    JOB_TECHNOLOGIES {
        uuid job_id FK
        bigint technology_id FK
        decimal confidence_score
    }
```

---
# Ligação à base de dados

A ligação à PostgreSQL foi centralizada em `data-pipeline/database/postgres.py` para evitar repetir configuração nos scrapers.
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

