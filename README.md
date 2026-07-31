# EPISTEME

> **An AI-powered research assistant for scientific literature analysis, knowledge discovery, and active learning.**

EPISTEME is a modern research platform that helps students, researchers, and professionals understand scientific papers more efficiently. It combines semantic search, citation-aware question answering, claim verification, structured summarization, and interactive knowledge visualization to transform lengthy research papers into actionable insights.

---

## Problem Statement

Scientific research papers are often lengthy, complex, and difficult to study efficiently. Researchers spend significant time identifying key findings, validating important claims, preparing notes, and creating study material. Traditional summarization tools frequently miss context or fail to maintain traceability to the original paper.

---

## Solution

EPISTEME streamlines the research workflow by providing an integrated environment for analyzing scientific literature. It extracts meaningful information from uploaded papers, enables context-aware question answering, verifies important claims, generates concise summaries, creates active-recall flashcards, and visualizes relationships between research concepts while maintaining references to the source document.

---

# Features

* Upload and analyze scientific research papers (PDF)
* Citation-aware Question Answering
* Multi-stage Claim Verification
* AI-generated Research Summaries
* Structured Research Brief Generation
* Automatic Flashcard Generation
* Interactive Concept Graph Visualization
* Semantic Search using Vector Embeddings
* Clean, responsive, and intuitive user interface

---

# Workflow

```text
Research Paper (PDF)
        │
        ▼
Text Extraction
        │
        ▼
Semantic Chunking
        │
        ▼
Vector Embedding Generation
        │
        ▼
Semantic Retrieval
        │
 ┌──────┼──────────────┐
 ▼      ▼              ▼
Question  Claim      Summary
Answering Verification Generation
 │        │              │
 └────────┼──────────────┘
          ▼
 Flashcards & Concept Graph
```

---

# System Architecture

```text
                 Research Paper (PDF)
                         │
                         ▼
                 PDF Text Extraction
                         │
                         ▼
                Semantic Chunking
                         │
                         ▼
             Vector Embedding Generation
                         │
                         ▼
                  Vector Database
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
 Citation-aware      Claim Engine     Summary Engine
 Question Answering                  & Brief Generator
        │                │                │
        └────────────────┼────────────────┘
                         ▼
              Interactive React Frontend
```

---

# Technology Stack

## Frontend

* React 19
* TypeScript
* Vite
* Tailwind CSS
* React Force Graph
* Lucide Icons

## Backend

* Python
* FastAPI
* Uvicorn
* ChromaDB
* Sentence Transformers
* PyMuPDF
* Pydantic

## AI & NLP

* Retrieval-Augmented Generation (RAG)
* Semantic Embeddings
* Chain-of-Verification (CoVe)
* Natural Language Processing

---

# Project Structure

```text
EPISTEME
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── routes/
├── storage/
├── tests/
│
├── ai_client.py
├── cove_pipeline.py
├── generators.py
├── ingest.py
├── main.py
├── schemas.py
├── vector_store.py
├── requirements.txt
└── README.md
```

---

# Getting Started

## Prerequisites

* Python 3.10+
* Node.js 18+

---

## Backend

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the backend server:

```bash
uvicorn main:app --reload --port 8000
```

API Documentation:

```text
http://localhost:8000/docs
```

---

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Application:

```text
http://localhost:5173
```

---

# API Overview

| Endpoint                          | Description                                  |
| --------------------------------- | -------------------------------------------- |
| **POST** `/upload`                | Upload and process research papers           |
| **GET** `/paper/{id}/metadata`    | Retrieve paper metadata                      |
| **POST** `/paper/{id}/claims`     | Extract verified claims                      |
| **POST** `/paper/{id}/flashcards` | Generate flashcards                          |
| **POST** `/paper/{id}/conceptmap` | Generate concept graph                       |
| **POST** `/paper/{id}/brief`      | Generate structured brief                    |
| **GET** `/paper/{id}/summary`     | Generate research summary                    |
| **GET** `/paper/{id}/limitations` | Extract limitations                          |
| **POST** `/paper/{id}/ask`        | Ask questions with citation-backed responses |

---

# Testing

Run the integration test suite:

```bash
python tests/test_api.py
```

---

# Highlights

* Modular and scalable architecture
* Fast semantic retrieval pipeline
* Citation-aware responses
* Interactive knowledge visualization
* Clean REST API design
* Responsive user experience
* Production-ready project structure
* Designed for efficient scientific literature exploration

---

# Future Scope

* Multi-paper comparative analysis
* Cross-paper citation graph
* Collaborative research workspace
* Offline inference support
* Export summaries and flashcards
* Personalized study recommendations
* Advanced literature review assistant

---

# License

This project is licensed under the **MIT License**.
