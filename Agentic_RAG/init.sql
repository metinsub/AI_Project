-- Initialize PostgreSQL database with pgvector extension for RAG Assistant
-- This script runs automatically when the PostgreSQL container starts

-- Enable pgvector extension for vector operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents table to store metadata and content
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100),
    file_size INTEGER,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    text_content TEXT,
    chunk_count INTEGER DEFAULT 0
);

-- Create document_chunks table to store text chunks and their embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_embedding vector(384), -- 384 dimensions for sentence-transformers/all-MiniLM-L6-v2
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Create unique constraint to prevent duplicate chunks
    UNIQUE(document_id, chunk_index)
);

-- Create index for fast vector similarity search
CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON document_chunks 
USING ivfflat (chunk_embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index for document lookup
CREATE INDEX IF NOT EXISTS chunks_document_id_idx ON document_chunks(document_id);

-- Insert initial test data (optional)
INSERT INTO documents (filename, content_type, file_size, text_content) VALUES 
('welcome.txt', 'text/plain', 100, 'Welcome to the RAG Assistant! This system can help you find information in your documents.')
ON CONFLICT DO NOTHING;
