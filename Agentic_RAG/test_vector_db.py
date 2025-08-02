#!/usr/bin/env python3
"""
Test script for Vector Database functionality
Run this after starting the Docker containers to verify everything works.
"""

import os
import sys
import time
from api.services.vector_service import VectorService

# Set environment variables for testing
os.environ['POSTGRES_HOST'] = 'localhost'
os.environ['POSTGRES_PORT'] = '5432'
os.environ['POSTGRES_DB'] = 'rag_assistant'
os.environ['POSTGRES_USER'] = 'postgres'
os.environ['POSTGRES_PASSWORD'] = 'your_secure_password_here'

def test_vector_database():
    """Test the vector database functionality step by step."""
    print("🚀 Testing Vector Database Setup...")
    print("=" * 50)
    
    # Initialize VectorService
    try:
        print("1. Initializing VectorService...")
        vector_service = VectorService()
        print("✅ VectorService initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize VectorService: {e}")
        return False
    
    # Health check
    try:
        print("\n2. Performing health check...")
        health = vector_service.health_check()
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   Database connected: {health.get('database_connected', False)}")
        print(f"   pgvector enabled: {health.get('pgvector_enabled', False)}")
        print(f"   Embedding model: {health.get('embedding_model', 'unknown')}")
        print(f"   Documents: {health.get('documents_count', 0)}")
        print(f"   Chunks: {health.get('chunks_count', 0)}")
        
        if health['status'] != 'healthy':
            print("❌ Health check failed")
            return False
        print("✅ Health check passed")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test storing chunks
    try:
        print("\n3. Testing chunk storage...")
        test_chunks = [
            "Dies ist ein Testdokument über Künstliche Intelligenz und maschinelles Lernen.",
            "RAG (Retrieval-Augmented Generation) kombiniert Informationsabruf mit Textgeneration.",
            "Vector-Datenbanken ermöglichen effiziente Ähnlichkeitssuchen in hochdimensionalen Räumen.",
            "PostgreSQL mit pgvector ist eine beliebte Lösung für Vector-Suche in Produktionsumgebungen."
        ]
        
        # Assume document_id = 1 exists (from init.sql)
        success = vector_service.store_chunks(document_id=1, chunks=test_chunks)
        if success:
            print(f"✅ Successfully stored {len(test_chunks)} test chunks")
        else:
            print("❌ Failed to store chunks")
            return False
            
    except Exception as e:
        print(f"❌ Error storing chunks: {e}")
        return False
    
    # Test similarity search
    try:
        print("\n4. Testing similarity search...")
        test_queries = [
            "Was ist künstliche Intelligenz?",
            "Wie funktioniert RAG?",
            "Vector Database Suche"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            results = vector_service.search_similar(query, limit=3, similarity_threshold=0.1)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"   {i}. Similarity: {result['similarity']:.3f}")
                    print(f"      Text: {result['text'][:100]}...")
                    print(f"      From: {result['filename']}")
            else:
                print("   No similar chunks found")
        
        print("✅ Similarity search completed")
        
    except Exception as e:
        print(f"❌ Error in similarity search: {e}")
        return False
    
    # Test index creation
    try:
        print("\n5. Testing index creation...")
        index_success = vector_service.create_index()
        if index_success:
            print("✅ Vector index created successfully")
        else:
            print("❌ Failed to create vector index")
            return False
            
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Vector Database is working correctly.")
    print("\nNext steps:")
    print("- Start your FastAPI application: docker-compose up")
    print("- Test the /health endpoint")
    print("- Try uploading documents via /ingest")
    print("- Query documents via /query")
    
    return True

if __name__ == "__main__":
    print("⚠️  Make sure Docker containers are running:")
    print("   docker-compose up -d postgres")
    print("\nWaiting 5 seconds for database to be ready...")
    time.sleep(5)
    
    success = test_vector_database()
    sys.exit(0 if success else 1)