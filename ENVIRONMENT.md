# Porque existe o `.env`

O ficheiro `.env` fica fora do repositório porque este projeto é público e não deve expor credenciais.
O `.env.example` serve como referência para os devs e mostra as variáveis necessárias sem valores reais.

# Ligação à base de dados

A ligação à PostgreSQL foi centralizada em `data-pipeline/database/postgres.py` para evitar repetir configuração nos scrapers.
Assim, a configuração fica num único sítio e é mais fácil de manter.

# Como evitamos empresas duplicadas

A tabela `companies` tem `UNIQUE(name)` porque o mesmo nome deve representar a mesma empresa ao longo da pipeline.
Quando a empresa já existe, o código reaproveita o registo em vez de criar outro igual.

# Como evitamos jobs duplicados

A tabela `jobs` tem `UNIQUE(source, external_id)` porque o mesmo anúncio pode aparecer várias vezes na mesma fonte.
Se já existir um registo com a mesma fonte e o mesmo identificador, o script faz update em vez de criar duplicados.

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

# Links base para testar

Indeed:
`https://www.indeed.com/jobs?q=python&l=Texas&radius=50&start=0`

LinkedIn:
`https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=web%20dev&start=0`

Estes links servem como base para testar a paginação e confirmar rapidamente se o scraper está a ler os dados correctos.
