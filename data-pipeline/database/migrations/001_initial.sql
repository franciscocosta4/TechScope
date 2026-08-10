CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    website TEXT,
    location TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES companies (id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    location TEXT,
    salary_min NUMERIC,
    salary_max NUMERIC,
    description TEXT,
    source TEXT NOT NULL,
    external_id TEXT NOT NULL,
    date_posted TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (source, external_id)
);

CREATE TABLE IF NOT EXISTS technologies (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS job_technologies (
    job_id UUID NOT NULL REFERENCES jobs (id) ON DELETE CASCADE,
    technology_id UUID NOT NULL REFERENCES technologies (id) ON DELETE CASCADE,
    confidence_score NUMERIC,
    PRIMARY KEY (job_id, technology_id)
);
