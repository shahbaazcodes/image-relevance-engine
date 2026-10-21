-- AI Image Understanding & Content Matching Engine — initial schema.
-- Creates the pgvector-backed image catalog used by hybrid search and the
-- Mismatch Guard. Seed rows provide a deterministic benchmark corpus.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    phash VARCHAR(64) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    caption TEXT,
    embedding vector(768),
    fts_vector tsvector,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_images_phash ON images(phash);
CREATE INDEX IF NOT EXISTS idx_images_fts ON images USING gin(fts_vector);
CREATE INDEX IF NOT EXISTS idx_images_category ON images(category);

-- Deterministic benchmark corpus: one row per evaluation query.
INSERT INTO images (filename, phash, category, caption, fts_vector)
VALUES
    ('fox_01.jpg', md5('fox_01.jpg'), 'fox', 'a red fox in the forest',
     to_tsvector('english', 'a red fox in the forest')),
    ('fox_02.jpg', md5('fox_02.jpg'), 'fox', 'fox running through grass',
     to_tsvector('english', 'fox running through grass')),
    ('fox_03.jpg', md5('fox_03.jpg'), 'fox', 'close-up of a fox face',
     to_tsvector('english', 'close-up of a fox face')),
    ('fox_04.jpg', md5('fox_04.jpg'), 'fox', 'wild fox at night',
     to_tsvector('english', 'wild fox at night')),
    ('fox_05.jpg', md5('fox_05.jpg'), 'fox', 'red fox sitting in snow',
     to_tsvector('english', 'red fox sitting in snow')),
    ('wolf_01.jpg', md5('wolf_01.jpg'), 'wolf', 'gray wolf howling at moon',
     to_tsvector('english', 'gray wolf howling at moon')),
    ('wolf_02.jpg', md5('wolf_02.jpg'), 'wolf', 'wolf pack in the woods',
     to_tsvector('english', 'wolf pack in the woods')),
    ('wolf_03.jpg', md5('wolf_03.jpg'), 'wolf', 'wolf running through snow',
     to_tsvector('english', 'wolf running through snow')),
    ('wolf_04.jpg', md5('wolf_04.jpg'), 'wolf', 'close-up of a wolf face',
     to_tsvector('english', 'close-up of a wolf face')),
    ('wolf_05.jpg', md5('wolf_05.jpg'), 'wolf', 'wild wolf standing on hill',
     to_tsvector('english', 'wild wolf standing on hill')),
    ('dog_01.jpg', md5('dog_01.jpg'), 'dog', 'golden retriever playing fetch',
     to_tsvector('english', 'golden retriever playing fetch')),
    ('dog_02.jpg', md5('dog_02.jpg'), 'dog', 'small dog barking at mailman',
     to_tsvector('english', 'small dog barking at mailman')),
    ('dog_03.jpg', md5('dog_03.jpg'), 'dog', 'puppy sleeping in bed',
     to_tsvector('english', 'puppy sleeping in bed')),
    ('dog_04.jpg', md5('dog_04.jpg'), 'dog', 'dog running in park',
     to_tsvector('english', 'dog running in park')),
    ('dog_05.jpg', md5('dog_05.jpg'), 'dog', 'bulldog on a leash',
     to_tsvector('english', 'bulldog on a leash')),
    ('deer_01.jpg', md5('deer_01.jpg'), 'deer', 'white-tailed deer in forest',
     to_tsvector('english', 'white-tailed deer in forest')),
    ('deer_02.jpg', md5('deer_02.jpg'), 'deer', 'deer grazing in meadow',
     to_tsvector('english', 'deer grazing in meadow')),
    ('deer_03.jpg', md5('deer_03.jpg'), 'deer', 'fawn with spots in grass',
     to_tsvector('english', 'fawn with spots in grass')),
    ('deer_04.jpg', md5('deer_04.jpg'), 'deer', 'stag with antlers',
     to_tsvector('english', 'stag with antlers')),
    ('deer_05.jpg', md5('deer_05.jpg'), 'deer', 'deer drinking from stream',
     to_tsvector('english', 'deer drinking from stream'))
ON CONFLICT (phash) DO NOTHING;