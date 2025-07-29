# Agentic RAG Business Assistant

Ein moderner AI-Business-Assistent basierend auf Retrieval-Augmented Generation (RAG) und LangChain Agents.

## 🎯 Projektübersicht

Das System kombiniert RAG mit Agentic AI, wodurch ein LLM selbstständig Tools nutzen kann:
- **Dokumentenverwaltung**: PDF-Upload und Verarbeitung
- **Intelligente Suche**: Vector-basierte Dokumentensuche  
- **Agentic Layer**: KI entscheidet zwischen verschiedenen Tools
- **REST-API**: FastAPI-basierte Schnittstelle

## 🏗️ Architektur

```
[User/Frontend] → [FastAPI Backend] → [LLM via OpenAI API]
                       ↓
                [PostgreSQL + pgvector]
                       ↓
                [LangChain Agent Tools]
```

## 🚀 API Endpoints

- `GET /health` - Systemstatus
- `POST /ingest` - Dokumente hochladen
- `POST /query` - RAG-basierte Fragen
- `POST /agent` - Agentic AI-Antworten

## 🛠️ Tech Stack

- **Backend**: FastAPI + Python 3.11+
- **AI Framework**: LangChain + OpenAI API
- **Database**: PostgreSQL + pgvector
- **Containerization**: Docker + docker-compose

## 📋 Setup (Coming Soon)

1. Clone Repository
2. Configure `.env` 
3. `docker-compose up`
4. Upload test documents
5. Start querying!

## 📁 Projektstruktur

```
agentic-rag-assistant/
├── api/                    # FastAPI Backend
│   ├── routes/            # API Endpoints
│   ├── services/          # Business Logic  
│   ├── models/            # Database Models
│   └── utils/             # Hilfsfunktionen
├── docker-compose.yml     # Container Setup
├── Dockerfile            # API Container
└── test_documents/       # PDF Test-Dateien
```

## 🔄 Development Status

- [x] Projektstruktur erstellt
- [ ] FastAPI Setup
- [ ] Docker Configuration  
- [ ] RAG Implementation
- [ ] Agent Integration
- [ ] Testing & Deployment 