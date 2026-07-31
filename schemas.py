from typing import List, Literal
from pydantic import BaseModel, Field


class Citation(BaseModel):
    text: str = Field(..., description="Verbatim quote from source text")
    page: int = Field(..., description="1-based page index")
    chunk_id: str = Field(..., description="Unique chunk UUID")
    page_display: str = Field(default="", description="Human-readable page range string")


class UploadResponse(BaseModel):
    paper_id: str = Field(..., description="Unique ID assigned to the uploaded paper")


class MetadataResponse(BaseModel):
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(..., description="List of paper authors")
    abstract: str = Field(..., description="Paper abstract")
    keywords: List[str] = Field(..., description="Keywords associated with the paper")
    is_fallback: bool = Field(default=False, description="True if fallback response was served")


class AskResponse(BaseModel):
    answer: str = Field(..., description="Synthesized grounded answer")
    citations: List[Citation] = Field(..., description="Supporting citations for the answer")
    is_fallback: bool = Field(default=False, description="True if fallback response was served")


class SummaryResponse(BaseModel):
    executive: str = Field(..., description="Executive summary")
    detailed: str = Field(..., description="Detailed technical breakdown")
    is_fallback: bool = Field(default=False, description="True if fallback response was served")


class ClaimEvidence(BaseModel):
    claim: str = Field(..., description="Extracted claim text")
    evidence: str = Field(..., description="Verbatim supporting quote")
    citation: Citation = Field(..., description="Source citation metadata")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Verification confidence score")


class ClaimsResponse(BaseModel):
    claims: List[ClaimEvidence] = Field(..., description="Extracted verified claims")
    is_fallback: bool = Field(default=False, description="True if fallback response was served")


class Limitation(BaseModel):
    limitation: str = Field(..., description="Identified paper limitation")
    citation: Citation = Field(..., description="Source citation metadata")


class LimitationsResponse(BaseModel):
    limitations: List[Limitation] = Field(..., description="List of paper limitations")
    is_fallback: bool = Field(default=False, description="True if fallback response was served")


class Flashcard(BaseModel):
    question: str = Field(..., description="Active recall question")
    answer: str = Field(..., description="Concise answer")
    difficulty: Literal["Easy", "Medium", "Hard"] = Field(..., description="Concept difficulty level")


class FlashcardsResponse(BaseModel):
    flashcards: List[Flashcard] = Field(..., description="Generated study flashcards")
    is_fallback: bool = Field(default=False, description="True if fallback response was served")


class Node(BaseModel):
    id: str = Field(..., description="Unique concept node ID")
    label: str = Field(..., description="Human-readable concept label")


class Edge(BaseModel):
    source: str = Field(..., description="Source concept node ID")
    target: str = Field(..., description="Target concept node ID")
    label: str = Field(..., description="Relationship label")


class ConceptMapResponse(BaseModel):
    nodes: List[Node] = Field(..., description="Graph concept nodes")
    edges: List[Edge] = Field(..., description="Graph relationship edges")
    is_fallback: bool = Field(default=False, description="True if fallback response was served")


class BriefResponse(BaseModel):
    problem: str = Field(..., description="Core research problem")
    method: str = Field(..., description="Methodology description")
    dataset: str = Field(..., description="Datasets used")
    results: str = Field(..., description="Key results summary")
    limitations: str = Field(..., description="Core limitations")
    future_work: str = Field(..., description="Future directions")
    contribution: str = Field(..., description="Primary research contribution")
    is_fallback: bool = Field(default=False, description="True if fallback response was served")
