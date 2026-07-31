const BASE_URL = "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      const errBody = await response.json().catch(() => ({}));
      throw new Error(errBody.detail || `HTTP error! status: ${response.status}`);
    }
    return await response.json() as T;
  } catch (err: any) {
    console.error(`API Error on path ${path}:`, err);
    throw new Error(err.message || "Network request failed. Ensure the server is running.");
  }
}

export const apiClient = {
  /**
   * Uploads a research paper PDF and returns its paper_id
   */
  async uploadPdf(file: File): Promise<{ paper_id: string }> {
    const formData = new FormData();
    formData.append("file", file);
    return request<{ paper_id: string }>("/upload", {
      method: "POST",
      body: formData,
    });
  },

  /**
   * Retrieves verified claims from the CoVe pipeline
   */
  async getClaims(paperId: string): Promise<any[]> {
    return request<any[]>(`/paper/${paperId}/claims`);
  },

  /**
   * Submits a user question to the RAG query engine
   */
  async askQuestion(paperId: string, question: string): Promise<{ answer: string; citations: any[] }> {
    return request<{ answer: string; citations: any[] }>(`/paper/${paperId}/ask`, {
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
  async getMetadata(paperId: string): Promise<{ title: string; authors: string[]; abstract: string; keywords: string[] }> {
    return request<{ title: string; authors: string[]; abstract: string; keywords: string[] }>(`/paper/${paperId}/metadata`);
  },

  /**
   * Retrieves executive and detailed summaries
   */
  async getSummary(paperId: string): Promise<{ executive: string; detailed: string }> {
    return request<{ executive: string; detailed: string }>(`/paper/${paperId}/summary`);
  },

  /**
   * Retrieves structured technical brief
   */
  async getBrief(paperId: string): Promise<{
    problem: string;
    method: string;
    dataset: string;
    results: string;
    limitations: string;
    future_work: string;
    contribution: string;
  }> {
    return request<{
      problem: string;
      method: string;
      dataset: string;
      results: string;
      limitations: string;
      future_work: string;
      contribution: string;
    }>(`/paper/${paperId}/brief`);
  },

  /**
   * Retrieves extracted paper limitations
   */
  async getLimitations(paperId: string): Promise<any[]> {
    return request<any[]>(`/paper/${paperId}/limitations`);
  },

  /**
   * Retrieves conceptual study flashcards
   */
  async getFlashcards(paperId: string): Promise<any[]> {
    return request<any[]>(`/paper/${paperId}/flashcards`);
  },

  /**
   * Retrieves concept nodes/edges for the knowledge map
   */
  async getConceptMap(paperId: string): Promise<{ nodes: any[]; edges: any[] }> {
    return request<{ nodes: any[]; edges: any[] }>(`/paper/${paperId}/conceptmap`);
  },
};
export default apiClient;
