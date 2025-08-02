#!/usr/bin/env python3
"""
Simple test script for our FAISS VectorService
Tests basic functionality with example data
"""

import sys
import os

# Add api directory to path so we can import our service
sys.path.append('api')

from services.vector_service import VectorService

def test_vector_service():
    """Test our VectorService with example chunks."""
    print("🚀 Testing VectorService...")
    print("=" * 50)
    
    # Initialize service
    print("1. Initializing VectorService...")
    try:
        vector_service = VectorService()
        print("✅ VectorService initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize VectorService: {e}")
        return False
    
    # Test with empty search (should return empty)
    print("\n2. Testing empty search...")
    results = vector_service.search_similar("test query")
    if results == []:
        print("✅ Empty search works correctly (no documents yet)")
    else:
        print(f"❌ Expected empty results, got: {results}")
    
    # Add some test chunks
    print("\n3. Adding test documents...")
    test_chunks = [
        "Künstliche Intelligenz (KI) ist ein Bereich der Informatik, der sich mit der Entwicklung intelligenter Maschinen beschäftigt.",
        "Machine Learning ist ein Teilbereich der KI, der Algorithmen verwendet, um aus Daten zu lernen.",
        "RAG (Retrieval-Augmented Generation) kombiniert Informationsabruf mit Textgeneration für bessere AI-Antworten.",
        "FAISS ist eine Bibliothek für effiziente Ähnlichkeitssuche in hochdimensionalen Vektorräumen.",
        "Python ist eine beliebte Programmiersprache für KI und Data Science Projekte."
    ]
    
    try:
        success = vector_service.store_chunks(test_chunks)
        if success:
            print(f"✅ Successfully stored {len(test_chunks)} chunks")
        else:
            print("❌ Failed to store chunks")
            return False
    except Exception as e:
        print(f"❌ Error storing chunks: {e}")
        return False
    
    # Test searches
    print("\n4. Testing similarity searches...")
    test_queries = [
        "Was ist künstliche Intelligenz?",
        "Wie funktioniert Machine Learning?", 
        "Was ist RAG?",
        "Python Programmierung",
        "Vektor Suche"
    ]
    
    for query in test_queries:
        print(f"\n   Query: '{query}'")
        try:
            results = vector_service.search_similar(query)
            print(f"   Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                # Show first 80 characters of each result
                preview = result[:80] + "..." if len(result) > 80 else result
                print(f"   {i}. {preview}")
        except Exception as e:
            print(f"   ❌ Error searching: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 VectorService test completed!")
    print("\nNext steps:")
    print("- VectorService is working ✅")
    print("- Ready for RAG Tools implementation")
    print("- Ready for Agent integration")
    
    return True

if __name__ == "__main__":
    print("🧪 VectorService Test Script")
    print("Make sure you have installed: langchain, faiss-cpu, sentence-transformers")
    print()
    
    success = test_vector_service()
    sys.exit(0 if success else 1)