import os
from typing import Dict, Any
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Import schemas from the shared schemas file
from schemas import (
    FlashcardsResponse,
    ConceptMapResponse,
    BriefResponse,
    SummaryResponse,
)

# Tenacity exponential backoff wrapper for Gemini API calls
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
def generate_content_with_retry(client: genai.Client, model: str, contents: Any, config: Any):
    return client.models.generate_content(model=model, contents=contents, config=config)

def _get_gemini_client() -> genai.Client:
    """
    Initializes and returns the Gemini API client.
    """
    return genai.Client()

def _get_flashcards_fallback() -> FlashcardsResponse:
    fallback_json = """
    {
      "flashcards": [
        {"question": "What is the core optimization model proposed in the paper?", "answer": "A Hybrid Quantum-Classical Neural Network (HQCNN) utilizing parameterized quantum circuits (PQCs).", "difficulty": "Medium"},
        {"question": "By what percentage does the HQCNN model reduce inventory costs compared to DQN?", "answer": "It reduces holding and stockout costs by 15% in high-uncertainty environments.", "difficulty": "Easy"},
        {"question": "How does amplitude encoding reduce qubit requirements?", "answer": "It maps a state with N variables onto log2(N) qubits, resulting in logarithmic qubit scaling.", "difficulty": "Hard"}
      ],
      "is_fallback": true
    }
    """
    return FlashcardsResponse.model_validate_json(fallback_json)

def generate_flashcards(verified_claims_json: str) -> FlashcardsResponse:
    """
    Ingests the verified claims JSON string and translates the facts into active-recall
    flashcard question-and-answer pairs, classified by difficulty.
    """
    if not os.environ.get("GEMINI_API_KEY"):
        return _get_flashcards_fallback()

    try:
        client = _get_gemini_client()
        
        prompt = (
            f"You are an academic study assistant. Ingest the following verified claims JSON from a research paper:\n\n"
            f"{verified_claims_json}\n\n"
            f"Generate a list of high-quality active-recall flashcards based ONLY on the claims in this JSON. "
            f"Each card must contain:\n"
            f"- question: A clear question probing a concept from the claims\n"
            f"- answer: A concise, precise answer to the question\n"
            f"- difficulty: 'Easy', 'Medium', or 'Hard' depending on the complexity of the concept.\n\n"
            f"Output must be a JSON object matching the FlashcardsResponse schema."
        )
        
        config = types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
            response_schema=FlashcardsResponse,
        )
        
        response = generate_content_with_retry(
            client=client,
            model="gemini-2.0-flash",
            contents=prompt,
            config=config
        )
        
        return FlashcardsResponse.model_validate_json(response.text)
    except Exception as e:
        print(f"Warning: Flashcards generation failed after retries ({e}). Serving fallback response.")
        return _get_flashcards_fallback()

def _get_conceptmap_fallback() -> ConceptMapResponse:
    fallback_json = """
    {
      "nodes": [
        {"id": "HQCNN", "label": "Hybrid Quantum-Classical Neural Network"},
        {"id": "PQC", "label": "Parameterized Quantum Circuits"},
        {"id": "DQN", "label": "Deep Q-Network (Classical)"},
        {"id": "Inventory_Opt", "label": "Inventory Optimization"}
      ],
      "edges": [
        {"source": "HQCNN", "target": "PQC", "label": "utilizes"},
        {"source": "HQCNN", "target": "Inventory_Opt", "label": "applies to"},
        {"source": "HQCNN", "target": "DQN", "label": "outperforms"}
      ],
      "is_fallback": true
    }
    """
    return ConceptMapResponse.model_validate_json(fallback_json)

def generate_conceptmap(verified_claims_json: str) -> ConceptMapResponse:
    """
    Ingests the verified claims JSON string, extracts key topological nodes (concepts/entities)
    and edges (relationships), formatting them for a force-directed graph visualization.
    """
    if not os.environ.get("GEMINI_API_KEY"):
        return _get_conceptmap_fallback()

    try:
        client = _get_gemini_client()
        
        prompt = (
            f"You are a network analysis assistant. Ingest the following verified claims JSON from a research paper:\n\n"
            f"{verified_claims_json}\n\n"
            f"Extract key topological entities (nodes: such as specific models, datasets, metrics, limitations) "
            f"and the relationships between them (edges: such as 'applies to', 'improves upon', 'tested on', 'causes'). "
            f"Return a structured concept map containing a list of nodes (id, label) and edges (source, target, label) "
            f"matching the ConceptMapResponse schema. Ensure all source and target references in edges map exactly to node IDs."
        )
        
        config = types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
            response_schema=ConceptMapResponse,
        )
        
        response = generate_content_with_retry(
            client=client,
            model="gemini-2.0-flash",
            contents=prompt,
            config=config
        )
        
        return ConceptMapResponse.model_validate_json(response.text)
    except Exception as e:
        print(f"Warning: Concept Map generation failed after retries ({e}). Serving fallback response.")
        return _get_conceptmap_fallback()

def _get_brief_fallback() -> BriefResponse:
    fallback_json = """
    {
      "problem": "Classical multi-echelon inventory optimization suffers from the curse of dimensionality under demand volatility.",
      "method": "Proposed a Hybrid Quantum-Classical Neural Network (HQCNN) using parameterized quantum circuits (PQCs).",
      "dataset": "Simulated global automotive supply chain dataset.",
      "results": "The proposed model converged 40% faster and reduced costs by 15% compared to classical DQN.",
      "limitations": "NISQ-era hardware limitations including low qubit counts and high gate error rates.",
      "future_work": "Investigate quantum error correction and multi-agent hybrid systems.",
      "contribution": "Demonstrated feasibility of parameterized quantum circuits for complex inventory decisions.",
      "is_fallback": true
    }
    """
    return BriefResponse.model_validate_json(fallback_json)

def generate_brief(verified_claims_json: str, metadata_json: str) -> BriefResponse:
    """
    Ingests both the verified claims JSON and paper metadata JSON, and synthesizes
    them into a highly structured technical brief.
    """
    if not os.environ.get("GEMINI_API_KEY"):
        return _get_brief_fallback()

    try:
        client = _get_gemini_client()
        
        prompt = (
            f"You are a research analysis lead. Ingest the following verified claims and metadata JSON objects:\n\n"
            f"Verified Claims JSON:\n{verified_claims_json}\n\n"
            f"Metadata JSON:\n{metadata_json}\n\n"
            f"Synthesize a highly structured technical brief of the paper isolating the following fields:\n"
            f"- problem: The main research problem or gap addressed by the study\n"
            f"- method: The methodology, architecture, and algorithms introduced/used\n"
            f"- dataset: The datasets utilized for training, evaluation, or benchmarking\n"
            f"- results: Key quantitative and qualitative results achieved\n"
            f"- limitations: Core constraints, assumptions, or issues identified\n"
            f"- future_work: Suggested directions for future research\n"
            f"- contribution: The primary significance and contribution of the work.\n\n"
            f"Ensure the output conforms exactly to the BriefResponse schema."
        )
        
        config = types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
            response_schema=BriefResponse,
        )
        
        response = generate_content_with_retry(
            client=client,
            model="gemini-2.0-flash",
            contents=prompt,
            config=config
        )
        
        return BriefResponse.model_validate_json(response.text)
    except Exception as e:
        print(f"Warning: Technical Brief generation failed after retries ({e}). Serving fallback response.")
        return _get_brief_fallback()

def _get_summary_fallback() -> SummaryResponse:
    fallback_json = """
    {
      "executive": "This study introduces a Hybrid Quantum-Classical Neural Network (HQCNN) to address the multi-echelon inventory optimization problem in supply chains. By combining classical deep reinforcement learning with parameterized quantum circuits, the framework offers a 15% cost reduction and 40% faster training convergence.",
      "detailed": "Traditional inventory optimization degrades under high-dimensional supply networks. This paper introduces HQCNN where the state space is mapped onto a quantum register using amplitude encoding. Evaluated on an automotive supply chain, the quantum model achieves tighter safety-stock bounds. However, NISQ gate errors and qubit counts restrict current scalability.",
      "is_fallback": true
    }
    """
    return SummaryResponse.model_validate_json(fallback_json)

def generate_summary(metadata_json: str, brief_json: str) -> SummaryResponse:
    """
    Ingests the metadata JSON and brief JSON, writing an executive summary (1-2 paragraphs)
    and a detailed technical summary (bulleted breakdown).
    """
    if not os.environ.get("GEMINI_API_KEY"):
        return _get_summary_fallback()

    try:
        client = _get_gemini_client()
        
        prompt = (
            f"You are an expert scientific editor. Ingest the following metadata and technical brief JSON objects:\n\n"
            f"Metadata JSON:\n{metadata_json}\n\n"
            f"Technical Brief JSON:\n{brief_json}\n\n"
            f"Synthesize two distinct summaries for the paper:\n"
            f"- executive: A cohesive executive summary (1-2 paragraphs, approx. 150-250 words) suitable for a general audience.\n"
            f"- detailed: A detailed, technical bulleted breakdown highlighting methodology details, results, limitations, and impact.\n\n"
            f"Ensure the output conforms exactly to the SummaryResponse schema."
        )
        
        config = types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
            response_schema=SummaryResponse,
        )
        
        response = generate_content_with_retry(
            client=client,
            model="gemini-2.0-flash",
            contents=prompt,
            config=config
        )
        
        return SummaryResponse.model_validate_json(response.text)
    except Exception as e:
        print(f"Warning: Summary generation failed after retries ({e}). Serving fallback response.")
        return _get_summary_fallback()
