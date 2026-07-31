# EPISTEME

EPISTEME is an open-source academic research engine designed for fact-grounded paper synthesis, claim verification, and active-recall study generation. It parses scientific literature, indexes semantic chunks with vector embeddings, and executes a multi-phase Chain-of-Verification (CoVe) pipeline to extract factually grounded claims backed by exact page-level citations.

---

## Key Features

- **Fact-Grounded Q&A (RAG)**: Asymmetric vector similarity retrieval using sentence-transformer embeddings with exact page and quote citations.
- **Chain-of-Verification (CoVe) Engine**: A 4-phase claim extraction pipeline that drafts, verifies against independent questions, and revises extracted claims to prevent hallucinations.
- **Active Recall Flashcards**: Automatically transforms verified paper claims into study flashcards categorized by difficulty.
- **Topological Concept Graphs**: Extracts entity nodes and relationship edges for interactive force-directed network visual analysis.
- **Structured Research Briefs & Summaries**: Synthesizes structured technical briefs and multi-level executive summaries directly from source text.

---

## Architecture

EPISTEME operates on a decoupled architecture separating text ingestion, local vector storage, inference orchestration, and the interactive UI layer.

```
                  +-----------------------+
                  |  PyMuPDF PDF Ingest   |
                  +-----------+-----------+
                              |
                              v
                  +-----------------------+
                  | Sentence-Transformers |
                  |  (BAAI/bge-small-en)  |
                  +-----------+-----------+
                              |
                              v
                  +-----------------------+
                  | Persistent ChromaDB   |
                  +-----------+-----------+
                              |
                              v
+------------------+  FastAPI  +-----------------------+
|  React Frontend  | <=======> |  CoVe Claim Engine    |
| (Vite, TS, Graph)|           |  & OpenRouter Models  |
+------------------+           +-----------------------+
```

---

## Tech Stack

### Backend
- **Framework**: Python 3.10+, FastAPI, Uvicorn
- **Vector DB & Embeddings**: ChromaDB, `sentence-transformers` (`BAAI/bge-small-en-v1.5`)
- **PDF Parsing**: PyMuPDF (`fitz`)
- **AI Orchestration**: OpenAI Python SDK configured for OpenRouter API, `tenacity` retry policy

### Frontend
- **Framework**: React 19, TypeScript, Vite
- **Styling**: Tailwind CSS v4, Lucide Icons
- **Visualization**: `react-force-graph-2d`

---

## Repository Structure

```
├── main.py                # FastAPI application entrypoint & middleware
├── ai_client.py           # OpenRouter client wrapper with model fallbacks
├── cove_pipeline.py       # 4-Phase Chain-of-Verification claim pipeline
├── generators.py          # Flashcard, concept map, brief, and summary generators
├── ingest.py              # PDF parsing and sentence-level semantic chunking
├── vector_store.py        # ChromaDB client & vector search module
├── schemas.py             # Pydantic data models & API schemas
├── routes/                # FastAPI endpoint handlers
│   └── paper.py           # Core paper ingestion, analytical, and RAG routes
├── tests/                 # Integration and sanity tests
│   └── test_api.py        # End-to-end API test suite
├── storage/               # Application storage (Chromadb, temporary files, cache)
├── frontend/              # React + TypeScript frontend application
│   ├── src/
│   │   ├── api/           # Frontend API client and TypeScript definitions
│   │   ├── components/    # UI components (Graph, Flashcards, Brief, Chat)
│   │   ├── App.tsx        # Main application layout
│   │   └── main.tsx       # React DOM entrypoint
│   ├── package.json
│   └── vite.config.ts
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher

### Environment Setup

Clone the repository and create a `.env` file in the project root based on `.env.example`:

```bash
cp .env.example .env
```

Define your OpenRouter API key in `.env`:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Installation & Running Locally

#### 1. Backend Setup

Initialize a Python virtual environment and install dependencies:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Start FastAPI development server
uvicorn main:app --reload --port 8000
```

The API documentation will be available at `http://127.0.0.1:8000/docs`.

#### 2. Frontend Setup

In a separate terminal, install dependencies and launch the dev server:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## API Overview

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `POST /upload` | `POST` | Uploads a PDF paper, parses chunks, and indexes embeddings into ChromaDB. |
| `GET /paper/{id}/metadata` | `GET` | Retrieves paper title, authors, abstract, and keywords. |
| `POST /paper/{id}/claims` | `POST` | Runs the 4-phase CoVe verification pipeline to extract grounded claims. |
| `POST /paper/{id}/flashcards` | `POST` | Generates active-recall flashcards from verified claims. |
| `POST /paper/{id}/conceptmap` | `POST` | Generates topological graph nodes and relationship edges. |
| `POST /paper/{id}/brief` | `POST` | Synthesizes a structured technical brief. |
| `GET /paper/{id}/summary` | `GET` | Generates executive and detailed technical summaries. |
| `GET /paper/{id}/limitations` | `GET` | Extracts paper constraints with source citations. |
| `POST /paper/{id}/ask` | `POST` | Performs grounded RAG Q&A with exact quote and page citations. |

---

## Verification & Testing

To run the automated integration test suite against a running local backend:

```bash
python tests/test_api.py
```

---

## Future Scope

- Multi-paper cross-referencing and literature comparative analysis.
- Anki export integration (.apkg format) for generated flashcards.
- Support for local offline LLM providers via Ollama / vLLM.

---

## License

Distributed under the MIT License. See `LICENSE` for details.
