# Porque existe o `.env`

O ficheiro `.env` fica fora do repositório porque este projeto é público e não deve expor credenciais.
O `.env.example` serve como referência para os devs e mostra as variáveis necessárias sem valores reais.

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

# Links base para testar

Indeed:
`https://pt.indeed.com/jobs?q=python&l=Porto&radius=50&start=0`

LinkedIn:
`https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=web%20dev&start=0`

## Filtros úteis

| Filtro           | LinkedIn / Google Jobs | Indeed            |
|------------------|------------------------|-------------------|
| Últimas 24h      | `f_TPR=r86400`         | `fromage=1`       |
| Última semana    | `f_TPR=r604800`        | `fromage=7`       |
| Full-time        | `f_JT=F`               | `jt=fulltime`     |
| Remote           | `f_WT=2`               | `remotejob=1`     |
| Júnior / Entry   | `f_E=2`                | `explvl=entry_level` |

