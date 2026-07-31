import os
import uuid
import json
import logging
import aiofiles
from typing import List, Dict, Any
from dotenv import load_dotenv
from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from pydantic import BaseModel

# Load environment variables
load_dotenv()

logger = logging.getLogger("episteme.routes.paper")

# Import schemas
from schemas import (
    UploadResponse,
    MetadataResponse,
    AskResponse,
    SummaryResponse,
    ClaimsResponse,
    LimitationsResponse,
    FlashcardsResponse,
    ConceptMapResponse,
    BriefResponse,
    Citation,
)

# Import module functions
from ingest import parse_pdf
from vector_store import VectorStore
from cove_pipeline import extract_verified_claims
from generators import (
    generate_flashcards,
    generate_conceptmap,
    generate_brief,
    generate_summary,
)

# Import centralized AI client
from ai_client import complete


# Input schema for Q&A
class AskRequest(BaseModel):
    question: str

router = APIRouter(prefix="", tags=["Paper"])

# Initialize directories
TEMP_DIR = "./storage/temp"
CACHE_DIR = "./storage/cache"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Initialize global VectorStore client
vector_store = VectorStore()

# Helper: Get cache paths
def _get_claims_cache_path(paper_id: str) -> str:
    return os.path.join(CACHE_DIR, f"{paper_id}_claims.json")

def _get_metadata_cache_path(paper_id: str) -> str:
    return os.path.join(CACHE_DIR, f"{paper_id}_metadata.json")

@router.post("/upload", response_model=UploadResponse)
async def upload_paper(file: UploadFile = File(...)):
    """
    Saves the uploaded PDF, parses it page-by-page, generates semantic chunks,
    and indexes them in ChromaDB.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File too large. Please upload a PDF under 10MB for the demo."
        )

    paper_id = str(uuid.uuid4())
    temp_file_path = os.path.join(TEMP_DIR, f"{paper_id}.pdf")
    
    # Save file asynchronously
    try:
        async with aiofiles.open(temp_file_path, "wb") as out_file:
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    # Ingest and parse PDF
    try:
        chunks = parse_pdf(temp_file_path)
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")
        
    # Index chunks in ChromaDB
    try:
        vector_store.add_paper(paper_id=paper_id, chunks=chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index paper: {str(e)}")
    finally:
        # Remove temp PDF file to save disk space
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    # Extract metadata from the first few chunks and cache it
    metadata_cache_path = _get_metadata_cache_path(paper_id)

    try:
        first_chunks = chunks[:3]
        combined_text = "\n\n".join([c["text"] for c in first_chunks])
        
        prompt = (
            f"Extract the metadata from the following introductory chunks of a paper:\n\n{combined_text}\n\n"
            f"Return a JSON object with: title (string), authors (list of strings), abstract (string), "
            f"and keywords (list of strings). Adhere strictly to the MetadataResponse schema."
        )
        response_text = complete(prompt=prompt, temperature=0.0, json_mode=True)
        
        # Cache metadata
        async with aiofiles.open(metadata_cache_path, "w", encoding="utf-8") as cache_file:
            await cache_file.write(response_text)
    except Exception as e:
        logger.error(f"Failed to auto-extract metadata: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Metadata extraction failed: {str(e)}"
        )

    return UploadResponse(paper_id=paper_id)

@router.get("/paper/{id}/metadata", response_model=MetadataResponse)
async def get_metadata(id: str):
    """
    Returns the cached metadata for the paper.
    """
    metadata_path = _get_metadata_cache_path(id)
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="Metadata not found. Upload the paper first.")
        
    async with aiofiles.open(metadata_path, "r", encoding="utf-8") as f:
        content = await f.read()
        return MetadataResponse.model_validate_json(content)

@router.post("/paper/{id}/claims", response_model=ClaimsResponse)
async def get_claims(id: str):
    """
    Retrieves chunks from the vector store, runs them through the 4-phase CoVe engine,
    caches the results, and returns the verified claims list.
    """
    # Verify collection exists in Chroma
    collection_name = vector_store._get_collection_name(id)
    try:
        collection = vector_store.client.get_collection(name=collection_name)
    except Exception:
        raise HTTPException(status_code=404, detail="Paper collection not found in vector store.")

    # Retrieve all chunks from collection
    raw_data = collection.get()
    if not raw_data or not raw_data.get("documents"):
        raise HTTPException(status_code=404, detail="No chunks found for the paper.")
        
    retrieved_chunks = []
    for idx in range(len(raw_data["documents"])):
        page = raw_data["metadatas"][idx].get("page", 1) if raw_data["metadatas"] and raw_data["metadatas"][idx] else 1
        retrieved_chunks.append({
            "chunk_id": raw_data["ids"][idx],
            "text": raw_data["documents"][idx],
            "page": page
        })
        
    # Execute CoVe Claims Pipeline
    try:
        claims_response = extract_verified_claims(retrieved_chunks)
    except Exception as e:
        logger.error(f"CoVe Engine failed: {e}")
        raise HTTPException(status_code=500, detail=f"CoVe Engine failed: {str(e)}")
        
    # Save output to cache
    claims_cache_path = _get_claims_cache_path(id)
    async with aiofiles.open(claims_cache_path, "w", encoding="utf-8") as cache_file:
        await cache_file.write(claims_response.model_dump_json())
        
    return claims_response

@router.post("/paper/{id}/flashcards", response_model=FlashcardsResponse)
async def get_flashcards(id: str):
    """
    Reads the cached claims JSON and generates flashcard question-and-answer pairs.
    """
    claims_path = _get_claims_cache_path(id)

    if not os.path.exists(claims_path):
        raise HTTPException(
            status_code=400, 
            detail="Claims must be generated first. Please call /paper/{id}/claims."
        )
        
    async with aiofiles.open(claims_path, "r", encoding="utf-8") as f:
        claims_json_str = await f.read()
        
    try:
        flashcards = generate_flashcards(claims_json_str)
        return flashcards
    except Exception as e:
        logger.error(f"Flashcard generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Flashcard generation failed: {str(e)}")

@router.post("/paper/{id}/conceptmap", response_model=ConceptMapResponse)
async def get_concept_map(id: str):
    """
    Reads the cached claims JSON and generates a nodes/edges concept map.
    """
    claims_path = _get_claims_cache_path(id)

    if not os.path.exists(claims_path):
        raise HTTPException(
            status_code=400, 
            detail="Claims must be generated first. Please call /paper/{id}/claims."
        )
        
    async with aiofiles.open(claims_path, "r", encoding="utf-8") as f:
        claims_json_str = await f.read()
        
    try:
        concept_map = generate_conceptmap(claims_json_str)
        return concept_map
    except Exception as e:
        logger.error(f"Concept map generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Concept map generation failed: {str(e)}")

@router.post("/paper/{id}/brief", response_model=BriefResponse)
async def get_brief(id: str):
    """
    Reads cached claims and metadata, generating a structured technical brief.
    """
    claims_path = _get_claims_cache_path(id)
    metadata_path = _get_metadata_cache_path(id)
    
    if not os.path.exists(claims_path) or not os.path.exists(metadata_path):
        raise HTTPException(
            status_code=400, 
            detail="Paper upload and claims extraction must be executed first."
        )
        
    async with aiofiles.open(claims_path, "r", encoding="utf-8") as cf:
        claims_json_str = await cf.read()
    async with aiofiles.open(metadata_path, "r", encoding="utf-8") as mf:
        metadata_json_str = await mf.read()
        
    try:
        brief = generate_brief(claims_json_str, metadata_json_str)
        # Cache brief for summary generation
        brief_cache_path = os.path.join(CACHE_DIR, f"{id}_brief.json")
        async with aiofiles.open(brief_cache_path, "w", encoding="utf-8") as bf:
            await bf.write(brief.model_dump_json())
        return brief
    except Exception as e:
        logger.error(f"Brief generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Brief generation failed: {str(e)}")

@router.get("/paper/{id}/summary", response_model=SummaryResponse)
async def get_summary(id: str):
    """
    Uses the cached metadata and brief to synthesize executive and detailed summaries.
    """
    metadata_path = _get_metadata_cache_path(id)
    brief_cache_path = os.path.join(CACHE_DIR, f"{id}_brief.json")
    
    # If brief doesn't exist, try to generate it first
    if not os.path.exists(brief_cache_path):
        try:
            await get_brief(id)
        except Exception:
            raise HTTPException(
                status_code=400, 
                detail="Brief and metadata must be available. Upload the paper and run claims first."
            )
            
    async with aiofiles.open(metadata_path, "r", encoding="utf-8") as mf:
        metadata_json_str = await mf.read()
    async with aiofiles.open(brief_cache_path, "r", encoding="utf-8") as bf:
        brief_json_str = await bf.read()
        
    try:
        summary = generate_summary(metadata_json_str, brief_json_str)
        return summary
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

@router.get("/paper/{id}/limitations", response_model=LimitationsResponse)
async def get_limitations(id: str):
    """
    Extracts paper limitations using OpenRouter API and returns a list.
    """
    collection_name = vector_store._get_collection_name(id)
    try:
        collection = vector_store.client.get_collection(name=collection_name)
    except Exception:
        raise HTTPException(status_code=404, detail="Paper collection not found in vector store.")

    # Retrieve all chunks
    raw_data = collection.get()
    if not raw_data or not raw_data.get("documents"):
        raise HTTPException(status_code=404, detail="No chunks found for the paper.")
        
    formatted_chunks_list = []
    for idx in range(len(raw_data["documents"])):
        chunk_id = raw_data["ids"][idx]
        page = raw_data["metadatas"][idx].get("page", 1) if raw_data["metadatas"] and raw_data["metadatas"][idx] else 1
        formatted_chunks_list.append(f"[Chunk ID: {chunk_id} | Page: {page}]\n{raw_data['documents'][idx]}")
    formatted_context = "\n\n".join(formatted_chunks_list)

    try:
        prompt = (
            f"Identify all core limitations, constraints, and boundaries mentioned in the following paper text:\n\n"
            f"{formatted_context}\n\n"
            f"Output MUST be a JSON object with format:\n"
            f'{{"limitations": [{{"limitation": "description of limitation", "citation": {{"text": "verbatim quote from text", "page": 1, "chunk_id": "..."}}}}]}}'
        )
        response_text = complete(prompt=prompt, temperature=0.0, json_mode=True)
        return LimitationsResponse.model_validate_json(response_text)
    except Exception as e:
        logger.error(f"Limitations extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Limitations extraction failed: {str(e)}")

@router.post("/paper/{id}/ask", response_model=AskResponse)
async def ask_question(id: str, request: AskRequest):
    """
    Performs vector similarity search to find relevant context, then synthesizes
    an answer verified with citations using OpenRouter with tenacity retry policy.
    """
    # 1. Query vector store for top 6 chunks matching question
    try:
        search_results = vector_store.search(paper_id=id, query=request.question, top_k=6)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")

    if not search_results:
        raise HTTPException(status_code=404, detail="No relevant content found in the database for this query.")

    try:
        # 2. Format retrieved chunks into context string with Chunk IDs and Page numbers
        formatted_chunks = []
        for item in search_results:
            formatted_chunks.append(
                f"[Chunk ID: {item['chunk_id']} | Page: {item['page']}]\n{item['text']}"
            )
        context_str = "\n\n".join(formatted_chunks)

        # 3. Formulate RAG prompt enforcing strict grounding and citations
        prompt = (
            f"You are a scientific Q&A assistant. Answer the user question based ONLY on the provided document context chunks.\n\n"
            f"DOCUMENT CONTEXT CHUNKS:\n{context_str}\n\n"
            f"USER QUESTION:\n{request.question}\n\n"
            f"Output MUST be a JSON object with format:\n"
            f'{{"answer": "Clear detailed answer", "citations": [{{"text": "verbatim quote supporting claim", "page": 1, "chunk_id": "..."}}]}}'
        )
        
        system_instruction = "Answer the following user question using ONLY the provided context chunks. You must provide exact verbatim quotes and page numbers for every claim in your answer."

        # 4. Execute using OpenRouter wrapped in tenacity exponential backoff retries
        response_text = complete(
            prompt=prompt,
            system_prompt=system_instruction,
            temperature=0.0,
            json_mode=True,
        )

        return AskResponse.model_validate_json(response_text)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RAG Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG Generation failed: {str(e)}")
