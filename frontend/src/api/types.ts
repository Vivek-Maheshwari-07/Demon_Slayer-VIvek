export interface Citation {
  text: string;
  page: number;
  chunk_id: string;
  page_display?: string;
}

export interface UploadResponse {
  paper_id: string;
}

export interface MetadataResponse {
  title: string;
  authors: string[];
  abstract: string;
  keywords: string[];
  isFallback: boolean;
}

export interface AskResponse {
  answer: string;
  citations: Citation[];
  isFallback: boolean;
}

export interface SummaryResponse {
  executive: string;
  detailed: string;
  isFallback: boolean;
}

export interface ClaimEvidence {
  claim: string;
  evidence: string;
  citation: Citation;
  confidence: number;
}

export interface ClaimsResponse {
  claims: ClaimEvidence[];
  isFallback: boolean;
}

export interface Limitation {
  limitation: string;
  citation: Citation;
}

export interface LimitationsResponse {
  limitations: Limitation[];
  isFallback: boolean;
}

export interface Flashcard {
  question: string;
  answer: string;
  difficulty: "Easy" | "Medium" | "Hard";
}

export interface FlashcardsResponse {
  flashcards: Flashcard[];
  isFallback: boolean;
}

export interface Node {
  id: string;
  label: string;
}

export interface Edge {
  source: string;
  target: string;
  label: string;
}

export interface ConceptMapResponse {
  nodes: Node[];
  edges: Edge[];
  isFallback: boolean;
}

export interface BriefResponse {
  problem: string;
  method: string;
  dataset: string;
  results: string;
  limitations: string;
  future_work: string;
  contribution: string;
  isFallback: boolean;
}
