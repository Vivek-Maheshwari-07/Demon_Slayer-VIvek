# Demon_Slayer-VIvek
# EPISTEME — 24H Build Roadmap (HackIndia Final Round)

## 0. Ground rules
- **API contract is locked at Hour 0** (see §2). Everyone codes against it in parallel from minute 1 — nobody waits on anybody.
- Frontend and Graph/Flashcard person use **mock JSON** matching the contract until backend endpoints are live. Swap mock→real at integration checkpoints.
- Git: one repo, branch per person (`feat/backend`, `feat/ai`, `feat/frontend`, `feat/graph`), merge to `main` at every checkpoint. No one works on `main` directly.
- Checkpoints: **Hr 4, Hr 9, Hr 16, Hr 20, Hr 23** — everyone stops, pulls, runs the full stack together for 15 min, fixes breakage immediately.

---

## 1. Roles (4 people)

| Role | Owns | Person |
|---|---|---|
| **A — Backend/Ingestion Lead** | FastAPI skeleton, PDF parsing, chunking, ChromaDB, upload/query endpoints | ___ |
| **B — AI/LLM Lead** | All Claude prompts: metadata, Q&A+citation, claims, limitations, flashcards, brief | ___ |
| **C — Frontend Lead** | React/TS/Tailwind: upload, chat, claims/limitations view, flashcards, brief view | ___ |
| **D — Graph & Integration Lead** | Concept map extraction+viz, flashcard UI wiring, demo script, bug-fixing across seams | ___ |

Rationale: **B and D never block on A** — B writes prompts against sample chunks locally, D builds graph JSON→viz against a hardcoded fixture. A and C are the only two doing "real" infra work, and they sync via the contract, not via each other's code.

---

## 2. API Contract (lock this first, 30 min, all 4 people in the room)

```
POST /upload                → {paper_id}
GET  /paper/{id}/metadata   → {title, authors, abstract, keywords}
POST /paper/{id}/ask        → body {question} → {answer, citations: [{text, page, chunk_id}]}
GET  /paper/{id}/summary    → {executive, detailed}
GET  /paper/{id}/claims     → [{claim, evidence, citation, confidence}]
GET  /paper/{id}/limitations→ [{limitation, citation}]
GET  /paper/{id}/flashcards → [{question, answer, difficulty}]
GET  /paper/{id}/conceptmap → {nodes: [{id,label}], edges: [{source,target,label}]}
GET  /paper/{id}/brief      → {problem, method, dataset, results, limitations, future_work, contribution}
```

Every citation object is `{text: "<exact quoted source sentence>", page: int, chunk_id: str}`. Every field that can't be found returns `"Not found in paper."` — never omit the key.

C and D build their UIs against this JSON shape starting now, using a static `fixtures/sample_response.json` A commits in the first 30 min.

---

## 3. Backend skeleton (Person A) — folder structure, build first

```
backend/
  main.py
  requirements.txt
  core/
    config.py
    chroma.py          # client + collection init
  ingestion/
    parser.py           # PyMuPDF extract text+pages
    chunker.py           # semantic chunk ~500 tok, keep page num per chunk
    embedder.py           # bge-small-en-v1.5 via sentence-transformers
  routes/
    upload.py
    query.py             # /ask, /summary, /claims, /limitations
    generate.py           # /flashcards, /conceptmap, /brief
  storage/
    papers/              # raw PDFs saved here, paper_id = uuid
  fixtures/
    sample_response.json
```

`requirements.txt`: `fastapi uvicorn python-multipart pymupdf sentence-transformers chromadb anthropic pydantic`

Retrieval: on `/ask`, embed question → Chroma `query(top_k=6)` → pass chunks+page numbers to Person B's prompt function → return.

---

## 4. AI/LLM prompt design (Person B)

One core principle for every prompt: **give Claude the chunks with page numbers inline, force it to quote verbatim, force `"Not found in paper."` when absent.** Same skeleton reused for claims/limitations/flashcards — only the extraction schema changes.

Prompts to write (as pure functions `chunks -> Claude call -> parsed JSON`, no FastAPI dependency, so B can test with fixture chunks immediately):

1. `extract_metadata(first_page_chunks)` → title/authors/abstract/keywords
2. `answer_question(question, retrieved_chunks)` → answer + citations (used by /ask)
3. `summarize(all_chunks)` → executive (1 para) + detailed
4. `extract_claims(all_chunks)` → list of {claim, evidence, citation, confidence 0-1}
5. `extract_limitations(all_chunks)` → list of {limitation, citation}
6. `generate_flashcards(claims + limitations)` → {question, answer, difficulty} — derive from claims already extracted, don't re-read the paper, saves a pass
7. `generate_conceptmap(claims + metadata)` → {nodes, edges} JSON — also derived, not a fresh paper read
8. `generate_brief(summary + claims + limitations)` → structured brief — derived, not fresh

**Key speed trick:** steps 6/7/8 consume the *outputs* of 3/4/5, not the raw paper. That's 3 LLM calls saved per paper and it's more grounded (less hallucination surface).

Verification (light CoVe, 1 pass only): after claims/limitations extraction, one follow-up Claude call: "here are claims + the exact chunks — flag any claim whose citation text does not actually support it." Drop or flag failures. Don't iterate further — no time.

All prompts use strict system prompt: quotes must be exact substrings of provided chunks; if you can't find it, output `"Not found in paper."`; never fabricate a citation.

---

## 5. Frontend (Person C)

```
frontend/src/
  api/client.ts          # typed fetch wrappers matching the contract
  types/index.ts          # shared TS interfaces from contract
  pages/
    Upload.tsx
    PaperView.tsx          # tabs: Chat | Summary | Claims | Limitations | Brief
  components/
    ChatPanel.tsx           # question box + answer + citation cards (click→highlight source text)
    ClaimsTable.tsx
    LimitationsList.tsx
    BriefView.tsx
```

Build against `fixtures/sample_response.json` first. Citation cards should show the exact quoted text + page number — that's a judge-visible "grounding" moment, make it prominent, not buried.

Skip: auth, multi-paper library, dark mode toggle, animations. Judges score grounding/citation/clarity, not polish.

---

## 6. Concept map + flashcards UI + integration (Person D)

- Concept map viz: use `react-force-graph-2d` or `vis-network` (fastest to wire, minimal config) — feed it the `/conceptmap` JSON directly, no NetworkX needed on frontend; NetworkX (if used at all) only for backend-side layout/export, skip if the JS lib does layout itself. **Recommendation: skip NetworkX entirely** — let the graph JS lib do force-directed layout, one less moving part.
- Flashcard UI: simple flip-card component, question/answer/difficulty badge, no spaced-repetition logic — just a static deck.
- From Hour 4 onward, D's second job is **integration firefighting**: sit at the seam between A/B (backend+AI) and C (frontend), catch contract drift immediately, run the app end-to-end every checkpoint.
- Hour 20+: owns the demo script — pick 1 paper, rehearse the exact click-path that shows grounding (ask a question → show citation → show flagged/verified claim → flashcards → concept map).

---

## 7. Hour-by-hour timeline

| Hrs | A (Backend) | B (AI) | C (Frontend) | D (Graph/Integration) |
|---|---|---|---|---|
| 0–0.5 | Lock API contract with everyone | same | same | same |
| 0.5–4 | FastAPI skeleton, upload, PyMuPDF parse, chunk, Chroma ingest | Write+test metadata & answer_question prompts on sample PDF chunks (local script, no server) | Scaffold app, build against fixture JSON | Build fixture conceptmap JSON, wire graph viz against it |
| **4 — checkpoint** | Upload+ingest working | Prompts return clean JSON | Upload UI + chat UI hitting fixtures | Graph renders from fixture |
| 4–9 | `/ask` endpoint wired to real retrieval+B's prompt | claims + limitations prompts | Wire ChatPanel to real `/ask`; build Claims/Limitations tabs | Wire flashcard/concept map to real backend as those land |
| **9 — checkpoint** | `/ask`, `/claims`, `/limitations` all real end-to-end | verification pass added | Chat + Claims + Limitations tabs fully live | Concept map still on fixture (blocked on B) — fine |
| 9–16 | `/flashcards`, `/conceptmap`, `/brief` endpoints (thin wrappers over B's functions) | flashcards, conceptmap, brief prompt functions | Brief view + flashcard UI polish | Concept map wired to real endpoint; flashcard flip UI done |
| **16 — checkpoint** | All 8 endpoints live | all 8 prompt functions done | All tabs live end-to-end | Full app runs start to finish once |
| 16–20 | Bug fixes, error handling (timeouts, bad PDFs), CORS | Prompt quality pass on 2-3 real test papers, tighten "Not found" behavior | Visual polish, loading states, citation highlight UX | Full regression pass, fix seams |
| **20 — checkpoint** | Freeze backend | Freeze prompts | Freeze frontend | Full demo run-through |
| 20–23 | On call for fires only | On call for fires only | On call for fires only | Demo script rehearsal, slides/talking points, pick best demo paper |
| 23–24 | Buffer | Buffer | Buffer | Final rehearsal, submission |

---

## 8. Cut list — do not touch unless everything above is done early
Neo4j, Qdrant, FSRS scheduling, multi-provider LLM failover, Celery/async queues, auth, multi-paper library, source-text PDF-embedded highlighting (a citation *card* with quoted text is enough — don't build a PDF viewer overlay unless hours remain).

---

Say the word and I'll start dropping actual code for whichever piece you want first — Backend skeleton (§3) is the right place to start since B and C's fixture work depends on the contract, not on A's code, so A can go first without blocking anyone.
