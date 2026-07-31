import type {
  UploadResponse,
  ClaimsResponse,
  AskResponse,
  MetadataResponse,
  SummaryResponse,
  BriefResponse,
  LimitationsResponse,
  FlashcardsResponse,
  ConceptMapResponse,
} from "./types";

export * from "./types";

const BASE_URL = "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      const errBody = await response.json().catch(() => ({}));
      throw new Error(errBody.detail || `HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    if (data && typeof data === "object" && !Array.isArray(data)) {
      if ("is_fallback" in data) {
        data.isFallback = Boolean(data.is_fallback);
      }
      if (data.isFallback || data.is_fallback) {
        window.dispatchEvent(new CustomEvent("episteme-fallback-detected"));
      }
    }
    return data as T;
  } catch (err: any) {
    console.error(`API Error on path ${path}:`, err);
    throw new Error(err.message || "Network request failed. Ensure the server is running.");
  }
}

export const apiClient = {
  /**
   * Uploads a research paper PDF and returns its paper_id
   */
  async uploadPdf(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append("file", file);
    return request<UploadResponse>("/upload", {
      method: "POST",
      body: formData,
    });
  },

  /**
   * Retrieves verified claims from the CoVe pipeline
   */
  async getClaims(paperId: string): Promise<ClaimsResponse> {
    return request<ClaimsResponse>(`/paper/${paperId}/claims`, { method: "POST" });
  },

  /**
   * Submits a user question to the RAG query engine
   */
  async askQuestion(paperId: string, question: string): Promise<AskResponse> {
    return request<AskResponse>(`/paper/${paperId}/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });
  },

  /**
   * Retrieves extracted document metadata
   */
  async getMetadata(paperId: string): Promise<MetadataResponse> {
    return request<MetadataResponse>(`/paper/${paperId}/metadata`);
  },

  /**
   * Retrieves executive and detailed summaries
   */
  async getSummary(paperId: string): Promise<SummaryResponse> {
    return request<SummaryResponse>(`/paper/${paperId}/summary`);
  },

  /**
   * Retrieves structured technical brief
   */
  async getBrief(paperId: string): Promise<BriefResponse> {
    return request<BriefResponse>(`/paper/${paperId}/brief`);
  },

  /**
   * Retrieves extracted paper limitations
   */
  async getLimitations(paperId: string): Promise<LimitationsResponse> {
    return request<LimitationsResponse>(`/paper/${paperId}/limitations`);
  },

  /**
   * Retrieves conceptual study flashcards
   */
  async getFlashcards(paperId: string): Promise<FlashcardsResponse> {
    return request<FlashcardsResponse>(`/paper/${paperId}/flashcards`, { method: "POST" });
  },

  /**
   * Retrieves concept nodes/edges for the knowledge map
   */
  async getConceptMap(paperId: string): Promise<ConceptMapResponse> {
    return request<ConceptMapResponse>(`/paper/${paperId}/conceptmap`, { method: "POST" });
  },
};

export default apiClient;
