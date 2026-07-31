import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger("episteme.generators")

# Import schemas from the shared schemas file
from schemas import (
    FlashcardsResponse,
    ConceptMapResponse,
    BriefResponse,
    SummaryResponse,
)

# Import centralized AI client
from ai_client import complete


def generate_flashcards(verified_claims_json: str) -> FlashcardsResponse:
    """
    Ingests the verified claims JSON string and translates the facts into active-recall
    flashcard question-and-answer pairs, classified by difficulty.
    """
    prompt = (
        f"You are an academic study assistant. Ingest the following verified claims JSON from a research paper:\n\n"
        f"{verified_claims_json}\n\n"
        f"Generate a list of high-quality active-recall flashcards based ONLY on the claims in this JSON. "
        f"Each card must contain:\n"
        f"- question: A clear question probing a concept from the claims\n"
        f"- answer: A concise, precise answer to the question\n"
        f"- difficulty: 'Easy', 'Medium', or 'Hard' depending on the complexity of the concept.\n\n"
        f"Output must be a JSON object strictly matching this format:\n"
        f'{{"flashcards": [{{"question": "...", "answer": "...", "difficulty": "Medium"}}]}}'
    )

    response_text = complete(prompt=prompt, json_mode=True)
    return FlashcardsResponse.model_validate_json(response_text)


def generate_conceptmap(verified_claims_json: str) -> ConceptMapResponse:
    """
    Ingests the verified claims JSON string, extracts key topological nodes (concepts/entities)
    and edges (relationships), formatting them for a force-directed graph visualization.
    """
    prompt = (
        f"You are a network analysis assistant. Ingest the following verified claims JSON from a research paper:\n\n"
        f"{verified_claims_json}\n\n"
        f"Extract key topological entities (nodes: such as specific models, datasets, metrics, limitations) "
        f"and the relationships between them (edges: such as 'applies to', 'improves upon', 'tested on', 'causes'). "
        f"Return a structured concept map containing a list of nodes (id, label) and edges (source, target, label) "
        f"matching the ConceptMapResponse schema. Ensure all source and target references in edges map exactly to node IDs.\n"
        f"Output must be a JSON object with 'nodes' and 'edges'."
    )

    response_text = complete(prompt=prompt, json_mode=True)
    return ConceptMapResponse.model_validate_json(response_text)


def generate_brief(verified_claims_json: str, metadata_json: str) -> BriefResponse:
    """
    Ingests both the verified claims JSON and paper metadata JSON, and synthesizes
    them into a highly structured technical brief.
    """
    prompt = (
        f"You are a research analysis lead. Ingest the following verified claims and metadata JSON objects:\n\n"
        f"Verified Claims JSON:\n{verified_claims_json}\n\n"
        f"Metadata JSON:\n{metadata_json}\n\n"
        f"Synthesize a highly structured technical brief of the paper. Output MUST be a JSON object where EVERY field is a plain STRING (use empty string \"\" if information is missing, do NOT use null or nested objects):\n"
        f"- problem: string describing the main research problem\n"
        f"- method: string describing the methodology and algorithms\n"
        f"- dataset: string describing the datasets used\n"
        f"- results: string summarizing key results\n"
        f"- limitations: string summarizing limitations\n"
        f"- future_work: string detailing future directions\n"
        f"- contribution: string detailing primary contribution\n\n"
        f'Example JSON format:\n{{"problem": "...", "method": "...", "dataset": "...", "results": "...", "limitations": "...", "future_work": "...", "contribution": "..."}}'
    )

    response_text = complete(prompt=prompt, json_mode=True)
    return BriefResponse.model_validate_json(response_text)


def generate_summary(metadata_json: str, brief_json: str) -> SummaryResponse:
    """
    Ingests the metadata JSON and brief JSON, writing an executive summary (1-2 paragraphs)
    and a detailed technical summary (bulleted breakdown).
    """
    prompt = (
        f"You are an expert scientific editor. Ingest the following metadata and technical brief JSON objects:\n\n"
        f"Metadata JSON:\n{metadata_json}\n\n"
        f"Technical Brief JSON:\n{brief_json}\n\n"
        f"Synthesize two distinct summaries for the paper. Output MUST be a JSON object with two string fields:\n"
        f"- executive: A single string containing a cohesive executive summary (1-2 paragraphs).\n"
        f"- detailed: A single string containing a detailed, bulleted technical breakdown using markdown formatting.\n\n"
        f'Example JSON format:\n{{"executive": "...", "detailed": "- Point 1\\n- Point 2"}}'
    )

    response_text = complete(prompt=prompt, json_mode=True)
    return SummaryResponse.model_validate_json(response_text)
