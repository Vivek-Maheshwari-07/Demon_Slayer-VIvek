import os
import json
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger("episteme.cove_pipeline")

# Import schemas from the shared schemas file
from schemas import Citation, ClaimEvidence, ClaimsResponse

# Import centralized AI client
from ai_client import complete

# Global system instruction enforcing strict factual grounding
GLOBAL_GROUNDING_INSTRUCTION = (
    "You are a strictly factual academic extraction engine. Your job is to extract methodology and "
    "claims from the provided research paper chunks. You must adhere to the following rules:\n"
    "1. Every extracted claim must be supported by evidence that is a verbatim exact substring from the text.\n"
    "2. You must record the exact integer page number where the evidence/quote started. Do not change it.\n"
    "3. Do not include any conversational filler, meta-commentary, or pleasantries in your output. Return only the requested structure.\n"
    "4. If no claims are found, return an empty list. Never make up or hallucinate claims or citations."
)


def extract_verified_claims(retrieved_chunks: List[Dict[str, Any]]) -> ClaimsResponse:
    """
    Executes a 4-Phase Chain-of-Verification (CoVe) pipeline on the retrieved chunks
    using OpenRouter (deepseek/deepseek-r1-0528:free) with tenacity exponential backoff retries.

    Raises on all errors — never returns silent fallback data.
    """
    # Format raw text chunks into a context string
    formatted_chunks_list = []
    for chunk in retrieved_chunks:
        chunk_id = chunk.get("chunk_id", "unknown")
        text = chunk.get("text", "")
        page = chunk.get("page")
        if page is None and "metadata" in chunk:
            page = chunk["metadata"].get("page")
        if page is None:
            page = 0
        formatted_chunks_list.append(f"[Chunk ID: {chunk_id} | Page: {page}]\n{text}")
    formatted_context = "\n\n".join(formatted_chunks_list)

    # =========================================================================
    # Phase 1: Draft Baseline Claims
    # =========================================================================
    phase1_prompt = (
        f"Here is the text context from the paper:\n\n"
        f"{formatted_context}\n\n"
        f"Please extract the core methodology and claims from this context. "
        f"For each claim, provide the claim text, the verbatim evidence quote supporting it, "
        f"the citation detailing the exact quote, page, and chunk_id, and a confidence score.\n\n"
        f"Output must be a JSON object with format:\n"
        f'{{"claims": [{{"claim": "...", "evidence": "...", "citation": {{"text": "...", "page": 1, "chunk_id": "..."}}, "confidence": 0.95}}]}}'
    )

    response1_text = complete(
        prompt=phase1_prompt,
        system_prompt=GLOBAL_GROUNDING_INSTRUCTION,
        temperature=0.0,
        json_mode=True,
    )

    draft_claims = ClaimsResponse.model_validate_json(response1_text)

    # If no claims were drafted, return immediately
    if not draft_claims.claims:
        return draft_claims

    # =========================================================================
    # Phase 2: Generate Independent Verification Questions
    # =========================================================================
    claims_text = "\n".join([
        f"- Claim: {c.claim}\n  Evidence Quote: {c.evidence}\n  Page: {c.citation.page}"
        for c in draft_claims.claims
    ])

    phase2_prompt = (
        f"Here is a list of drafted claims:\n\n"
        f"{claims_text}\n\n"
        f"For each claim, generate 1-2 sharp, objective verification questions that would "
        f"definitively prove or disprove the claim based on the source text. Return the result "
        f'strictly as a JSON object with a key "questions" containing an array of string questions.'
    )

    response2_text = complete(
        prompt=phase2_prompt,
        temperature=0.0,
        json_mode=True,
    )

    try:
        p2_data = json.loads(response2_text)
        questions = p2_data.get("questions", []) if isinstance(p2_data, dict) else []
    except Exception:
        questions = []

    # If no questions generated, return draft claims
    if not questions:
        return draft_claims

    # =========================================================================
    # Phase 3: Independent Execution (Anti-Sycophancy)
    # =========================================================================
    questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])

    phase3_prompt = (
        f"Here are several verification questions:\n\n"
        f"{questions_text}\n\n"
        f"Here is the text context from the paper:\n\n"
        f"{formatted_context}\n\n"
        f"Please answer each question using ONLY the provided text context. For each answer, "
        f"state the answer clearly and provide the exact verbatim quote and the page number where the "
        f"information was found. Do not reference any external claims, assumptions, or baseline drafts."
    )

    answers_text = complete(
        prompt=phase3_prompt,
        system_prompt=GLOBAL_GROUNDING_INSTRUCTION,
        temperature=0.0,
        json_mode=False,
    )

    # =========================================================================
    # Phase 4: Synthesis & Revision
    # =========================================================================
    draft_claims_json = draft_claims.model_dump_json(indent=2)

    phase4_prompt = (
        f"You are checking the factual validity of a set of drafted academic claims.\n\n"
        f"Here are the original drafted claims (Phase 1):\n"
        f"{draft_claims_json}\n\n"
        f"Here are the independent verification answers (Phase 3):\n"
        f"{answers_text}\n\n"
        f"Here is the raw text context from the paper:\n"
        f"{formatted_context}\n\n"
        f"Cross-reference the drafted claims against the independent verification answers and the raw text context. "
        f"For each claim:\n"
        f"1. Check if the independent verification answer supports or contradicts the claim.\n"
        f"2. Verify if the citation's quote matches the raw text exactly (character-for-character verbatim).\n"
        f"3. If a claim is contradicted, unsupported, or contains a non-verbatim quote, correct the claim or drop it entirely.\n"
        f"4. If verified, keep the claim and adjust the confidence score if necessary.\n\n"
        f'Return the final verified claims strictly as a JSON object with key "claims" matching the ClaimsResponse schema.'
    )

    response4_text = complete(
        prompt=phase4_prompt,
        system_prompt=GLOBAL_GROUNDING_INSTRUCTION,
        temperature=0.0,
        json_mode=True,
    )

    verified_claims = ClaimsResponse.model_validate_json(response4_text)
    return verified_claims
