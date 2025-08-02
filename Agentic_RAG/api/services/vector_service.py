# Clean imports - only what we actually use
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document



class VectorService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        self.vector_store = None  # Wird erstellt wenn erste Dokumente kommen
    
    def create_index(self):
        pass
    
    def store_chunks(self, chunks):
        # Schritt 1: Leere Liste für Documents
        documents = []
        
        # Schritt 2: Jeden String-Chunk in ein Document-Objekt umwandeln
        for chunk in chunks:
            doc = Document(page_content=chunk)
            documents.append(doc)
        
        # Schritt 3: FAISS mit Documents erstellen
        vector_store = FAISS.from_documents(
            documents=documents,  # Jetzt die Document-Objekte!
            embedding=self.embeddings
        )
        
        # Schritt 4: In der Instanz speichern (überschreibt immer)
        self.vector_store = vector_store
        
        # Optional: Erfolg zurückgeben
        return True
    
    
    def search_similar(self, query):
        # Schritt 1: Prüfen ob Vector Store existiert
        if self.vector_store is None:
            print("Kein Vector Store vorhanden. Erst Dokumente hinzufügen!")
            return []
        
        # Schritt 2:
        similar_docs = self.vector_store.similarity_search(query, k=2)
        
        # Schritt 3: Ergebnisse formatieren
        results = []
        for doc in similar_docs:
            results.append(doc.page_content)  # Nur den Text
        
        return results
        
        

