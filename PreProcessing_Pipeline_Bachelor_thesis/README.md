# RAG Preprocessing Pipeline

Dieses Projekt implementiert eine Preprocessing-Pipeline zur Verarbeitung technischer PDF-Dokumente für den Einsatz in Retrieval-Augmented Generation (RAG)-Systemen.

---

## Funktionen

- Extraktion von PDF-Inhalten mittels PyMuPDF (inkl. Header-Erkennung)
- Tokenbasiertes Chunking mit dem LangChain TextSplitter
- Abschnittsweise Umformulierung und Qualitätsbewertung durch ein Large Language Model (LLM) über die Ollama API
- Export der Ergebnisse im PDF-Format (Originaltext und qualitätsgeprüfte Umformulierung pro Abschnitt)
- Vollständig automatisierter, skriptgesteuerter Workflow über `main.py`

---

## Projektstruktur

```bash
PreProcessingBA/
├── main.py                    # Einstiegspunkt für die Verarbeitung
├── config.json                # Modell- und Token-Einstellungen
├── .env                       # Umgebungsvariablen (z.B. OLLAMA_API_URL)
├── requirements.txt           # Abhängigkeiten
├── data/
│   ├── input/                 # Eingabepfad für PDF-Dateien
│   ├── output/                # Ausgabeordner für verarbeitete PDFs
│   └── extracted/             # Temporärer Ordner für extrahierte Daten
├── logs/                      # Protokollierung von Fehlern und Fortschritt
├── prompts/                   # Prompt-Vorlagen für das LLM
│   ├── evaluator_prompt.txt   # Prompt für den Evaluator
│   ├── feedback_prompt.txt    # Prompt für feedback-basiertes Rephrasing
│   └── rephraser_prompt.txt   # Prompt für den Rephraser
├── scripts/
│   ├── pipeline.py            # Hauptlogik: Extraktion, Chunking, Umformulierung, Evaluierung & Export
│   ├── extractor.py           # PDF-Parsing (Header, Text, Seiten)
│   ├── exporter.py            # Exportfunktionen für PDF
│   ├── evaluation/            # Wrapper für Umformulierungsversuche und Evaluierung
│   │   ├── eval_output.py     # Enthält rephrase_with_evaluation Funktion
│   │   ├── evaluator.py       # Logik zur Evaluierung der Umformulierungen
│   │   ├── evaluator_schema.json # JSON-Schema für die Evaluator-Ausgabe
│   │   ├── parsed_evaluator.py # Parser für die Evaluator-Ausgabe
│   │   ├── metrics.json       # Konfiguration der Bewertungsmetriken
│   │   └── eval_config.json   # Konfiguration für die Evaluierung
│   └── processing/            # Kern-Verarbeitungsschritte
│       ├── rephraser.py       # LLM-Abfrage für Umformulierung
│       ├── chunker.py         # Chunking-Logik
│       └── tokenizer.py       # Tokenizer für das Chunking
├── tokenization_model/        # (Falls noch genutzt, sonst entfernen)
│   └── mistralai/
│       ├── special_tokens_map.json
│       ├── tokenizer_config.json
│       └── tokenizer.json
```

---

## Setup

**1. Installation**

```bash
pip install -r requirements.txt
```

**2. Konfiguration**

Erstellen Sie eine `.env`-Datei mit den notwendigen API-Informationen:

```
OLLAMA_API_URL= path.zur.url
```

**3. Ausführung**

```bash
python main.py --input data/input/dein_dokument.pdf
```
Der Ausgabepfad ist im Skript definiert (z.B. `data/output/`).

---

## Ausgabeformate

**PDF-Datei**

Abschnittsweise Darstellung mit:
- Kapitelüberschrift
- Generierter Umformulierung (qualitätsgeprüft)

(Hinweis: JSON-Ausgabe wurde aus der Beschreibung entfernt, da die Pipeline direkt PDF erzeugt)

## Zielsetzung

Die Pipeline wurde im Rahmen einer Bachelorarbeit entwickelt. Ziel ist die Erstellung eines skalierbaren, transparenten und reproduzierbaren Workflows zur Vorbereitung technischer Dokumente für RAG-Systeme.