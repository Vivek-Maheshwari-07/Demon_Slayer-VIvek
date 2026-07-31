from typing import List, Literal
from pydantic import BaseModel, Field, RootModel

class Citation(BaseModel):
    text: str = Field(..., description="The exact verbatim quote from the text")
    page: int = Field(..., description="The integer page number")
    chunk_id: str = Field(..., description="The UUID of the chunk")

class UploadResponse(BaseModel):
    paper_id: str = Field(..., description="Unique identifier for the uploaded paper")

class MetadataResponse(BaseModel):
    title: str = Field(..., description="Title of the paper")
    authors: List[str] = Field(..., description="List of authors")
    abstract: str = Field(..., description="Abstract of the paper")
    keywords: List[str] = Field(..., description="Keywords associated with the paper")

class AskResponse(BaseModel):
    answer: str = Field(..., description="Answer generated from the query")
    citations: List[Citation] = Field(..., description="List of citations verifying the answer")

class SummaryResponse(BaseModel):
    executive: str = Field(..., description="Executive summary (1 paragraph)")
    detailed: str = Field(..., description="Detailed summary")

class ClaimEvidence(BaseModel):
    claim: str = Field(..., description="Extracted claim from the text")
    evidence: str = Field(..., description="Verbatim evidence/context supporting the claim")
    citation: Citation = Field(..., description="Citation details for the evidence")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")

class ClaimsResponse(RootModel[List[ClaimEvidence]]):
    pass

class Limitation(BaseModel):
    limitation: str = Field(..., description="Identified limitation of the paper")
    citation: Citation = Field(..., description="Citation details for the limitation")

class LimitationsResponse(RootModel[List[Limitation]]):
    pass

class Flashcard(BaseModel):
    question: str = Field(..., description="Question for study")
    answer: str = Field(..., description="Answer for the question")
    difficulty: Literal["Easy", "Medium", "Hard"] = Field(..., description="Difficulty level")

class FlashcardsResponse(RootModel[List[Flashcard]]):
    pass

class Node(BaseModel):
    id: str = Field(..., description="Unique node ID (e.g., entity or concept)")
    label: str = Field(..., description="Human-readable label for the node")

class Edge(BaseModel):
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: str = Field(..., description="Relationship label")

class ConceptMapResponse(BaseModel):
    nodes: List[Node] = Field(..., description="List of concepts (nodes) in the graph")
    edges: List[Edge] = Field(..., description="List of relations (edges) between concepts")

class BriefResponse(BaseModel):
    problem: str = Field(..., description="The main research problem")
    method: str = Field(..., description="Methodology and approaches used")
    dataset: str = Field(..., description="Datasets used or collected")
    results: str = Field(..., description="Key results and achievements")
    limitations: str = Field(..., description="Core limitations identified")
    future_work: str = Field(..., description="Suggested future directions")
    contribution: str = Field(..., description="Main contribution of the work")
