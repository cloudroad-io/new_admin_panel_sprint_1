
CREATE SCHEMA IF NOT EXISTS content;

-- Table: genre
CREATE TABLE IF NOT EXISTS content.genre (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created TIMESTAMP WITH TIME ZONE,
    modified TIMESTAMP WITH TIME ZONE
);

-- Table: film_work
CREATE TABLE IF NOT EXISTS content.film_work (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE,
    modified TIMESTAMP WITH TIME ZONE
);

-- Table: person
CREATE TABLE IF NOT EXISTS content.person (
    id UUID PRIMARY KEY,
    full_name TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE,
    modified TIMESTAMP WITH TIME ZONE
);

-- Table: genre_film_work (many-to-many relationship between genre and film_work)
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id UUID PRIMARY KEY,
    genre_id UUID NOT NULL REFERENCES content.genre(id) ON DELETE CASCADE,
    film_work_id UUID NOT NULL REFERENCES content.film_work(id) ON DELETE CASCADE,
    created TIMESTAMP WITH TIME ZONE,
    UNIQUE (genre_id, film_work_id)
);

-- Table: person_film_work (many-to-many relationship between person and film_work)
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id UUID PRIMARY KEY,
    person_id UUID NOT NULL REFERENCES content.person(id) ON DELETE CASCADE,
    film_work_id UUID NOT NULL REFERENCES content.film_work(id) ON DELETE CASCADE,
    role TEXT,
    created TIMESTAMP WITH TIME ZONE,
    UNIQUE (person_id, film_work_id, role)
);

-- Indexes for optimization
CREATE INDEX IF NOT EXISTS idx_film_work_creation_date ON content.film_work (creation_date);
CREATE INDEX IF NOT EXISTS idx_film_work_rating ON content.film_work (rating);
CREATE INDEX IF NOT EXISTS idx_person_full_name ON content.person (full_name);
CREATE INDEX IF NOT EXISTS idx_genre_name ON content.genre (name);
