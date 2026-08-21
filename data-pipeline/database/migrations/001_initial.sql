-- Migration inicial: schema completo da base de dados TechScope.
-- Inclui tabelas base e tabela de keywords extraídas de descrições.

CREATE TABLE IF NOT EXISTS "Companies" (
    "Id" UUID PRIMARY KEY,
    "Name" TEXT NOT NULL UNIQUE,
    "Website" TEXT,
    "Location" TEXT,
    "CreatedAt" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "Jobs" (
    "Id" UUID PRIMARY KEY,
    "CompanyId" UUID NOT NULL REFERENCES "Companies" ("Id") ON DELETE CASCADE,
    "Title" TEXT NOT NULL,
    "Location" TEXT,
    "Source" TEXT NOT NULL,
    "ExternalId" TEXT NOT NULL,
    "DatePosted" DATE,
    "CreatedAt" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE ("Source", "ExternalId")
);

CREATE TABLE IF NOT EXISTS "JobKeywords" (
    "JobId" UUID NOT NULL REFERENCES "Jobs" ("Id") ON DELETE CASCADE,
    "Keyword" VARCHAR(100) NOT NULL,
    "Category" VARCHAR(50) NOT NULL,
    PRIMARY KEY ("JobId", "Keyword", "Category")
);

-- Índice para queries por categoria (ex: todas as vagas senior)
CREATE INDEX IF NOT EXISTS "IX_JobKeywords_Category" ON "JobKeywords" ("Category");

-- Índice para queries por keyword (ex: todas as vagas que mencionam "react")
CREATE INDEX IF NOT EXISTS "IX_JobKeywords_Keyword" ON "JobKeywords" ("Keyword");
