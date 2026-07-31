import uuid
from typing import List
from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import schemas
from schemas import (
    UploadResponse,
    MetadataResponse,
    AskResponse,
    SummaryResponse,
    ClaimsResponse,
    ClaimEvidence,
    LimitationsResponse,
    Limitation,
    FlashcardsResponse,
    Flashcard,
    ConceptMapResponse,
    Node,
    Edge,
    BriefResponse,
    Citation,
)

# Input schema for Q&A
class AskRequest(BaseModel):
    question: str

app = FastAPI(
    title="EPISTEME Module 0 Mock Server",
    description="Mock API endpoints for the academic research companion frontend integration.",
    version="1.0.0",
)

# Enable CORS for all origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared Mock Data Constants reflecting "Quantum Machine Learning in Supply Chain"
MOCK_PAPER_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

MOCK_METADATA = MetadataResponse(
    title="Quantum Machine Learning in Supply Chain: Optimizing Multi-Echelon Inventory Under Demand Uncertainty",
    authors=[
        "Dr. Evelyn Thorne (Quantum Technologies Lab)",
        "Prof. Marcus Vance (Institute for Supply Chain Excellence)",
        "Dr. Alan Turing Jr. (Department of Advanced Analytics)"
    ],
    abstract=(
        "This paper presents a novel approach to the multi-echelon inventory optimization problem "
        "in supply chain management using Quantum Machine Learning (QML). Traditional heuristic and "
        "classical reinforcement learning models struggle with the curse of dimensionality when scaling "
        "to global supply networks with volatile, non-Gaussian demand distributions. We propose a "
        "Hybrid Quantum-Classical Neural Network (HQCNN) utilizing parameterized quantum circuits (PQCs) "
        "to predict optimal reorder points and safety stock levels. Our model is trained on a simulated "
        "global automotive supply chain dataset. We demonstrate that HQCNN converges 40% faster and "
        "exhibits a 15% reduction in total holding and stockout costs compared to classical deep "
        "Q-networks (DQN) in noisy, high-uncertainty regimes. Finally, we analyze the limitations "
        "of current NISQ-era quantum hardware, specifically gate fidelity and qubit coherence times, "
        "and propose mitigation strategies for near-term industrial deployment."
    ),
    keywords=[
        "Quantum Machine Learning",
        "Supply Chain Optimization",
        "Multi-Echelon Inventory",
        "Parameterized Quantum Circuits",
        "NISQ Era"
    ]
)

# Standard mock citations used across endpoints
CITATION_1 = Citation(
    text="We propose a Hybrid Quantum-Classical Neural Network (HQCNN) utilizing parameterized quantum circuits (PQCs) to predict optimal reorder points and safety stock levels.",
    page=4,
    chunk_id="8d7b3e0c-3bf2-4ef8-a461-12c8ff457912"
)

CITATION_2 = Citation(
    text="We demonstrate that HQCNN converges 40% faster and exhibits a 15% reduction in total holding and stockout costs compared to classical deep Q-networks (DQN) in noisy, high-uncertainty regimes.",
    page=7,
    chunk_id="1c7a52f9-90b4-4e2b-8a58-e4b2a8d5423a"
)

CITATION_3 = Citation(
    text="By leveraging amplitude encoding, a supply chain state containing N variables can be mapped onto log2(N) qubits, drastically reducing representation space size.",
    page=3,
    chunk_id="2a7b8e5c-19c2-40f4-bde4-6b64ff1bcf23"
)

CITATION_4 = Citation(
    text="Finally, we analyze the limitations of current NISQ-era quantum hardware, specifically gate fidelity and qubit coherence times, and propose mitigation strategies for near-term industrial deployment.",
    page=1,
    chunk_id="ff8129a0-6218-4a5f-9db0-f5a6df912a7d"
)

CITATION_5 = Citation(
    text="Physical execution was limited to 8 qubits due to physical hardware availability, meaning larger scale multi-echelon graphs must be partitioned classically.",
    page=9,
    chunk_id="3b8a92c3-4d8e-4903-8822-1b1a772c918a"
)

@app.post("/upload", response_model=UploadResponse, tags=["Ingestion"])
async def upload_paper(file: UploadFile = File(...)):
    """
    Accepts a dummy multipart/form-data PDF file and returns a mock paper ID.
    """
    # For a mock server, we simply generate a random UUID and return it.
    paper_id = str(uuid.uuid4())
    return UploadResponse(paper_id=paper_id)

@app.get("/paper/{id}/metadata", response_model=MetadataResponse, tags=["Analysis"])
async def get_metadata(id: str):
    """
    Returns the metadata for the specified paper.
    """
    return MOCK_METADATA

@app.post("/paper/{id}/ask", response_model=AskResponse, tags=["Interaction"])
async def ask_question(id: str, request: AskRequest):
    """
    Accepts a question and returns a mock answer supported by matching citations.
    """
    question_lower = request.question.lower()
    
    # We return dynamic mock responses based on key keywords in the question, or a general default answer.
    if "converge" in question_lower or "speed" in question_lower or "performance" in question_lower:
        return AskResponse(
            answer="According to the paper, the proposed HQCNN model converges 40% faster during training compared to traditional deep Q-networks (DQN) in noisy environments.",
            citations=[CITATION_2]
        )
    elif "cost" in question_lower or "inventory" in question_lower or "saving" in question_lower:
        return AskResponse(
            answer="The hybrid model demonstrates a 15% reduction in total inventory holding and stockout costs by optimizing reorder points and safety stock levels under high demand uncertainty.",
            citations=[CITATION_1, CITATION_2]
        )
    elif "qubit" in question_lower or "encoding" in question_lower or "representation" in question_lower:
        return AskResponse(
            answer="The model utilizes amplitude encoding to map a supply chain state of N variables onto log2(N) qubits, allowing for logarithmic scaling of the state representation size.",
            citations=[CITATION_3]
        )
    else:
        # Default fallback response containing standard details
        return AskResponse(
            answer=(
                "The paper proposes a Hybrid Quantum-Classical Neural Network (HQCNN) that leverages parameterized "
                "quantum circuits (PQCs) to solve the multi-echelon inventory optimization problem. In noisy, "
                "high-uncertainty environments, it outperforms classical Deep Q-Networks (DQN) in both convergence "
                "speed (40% faster) and cost efficiency (15% reduction in total operational costs)."
            ),
            citations=[CITATION_1, CITATION_2]
        )

@app.get("/paper/{id}/summary", response_model=SummaryResponse, tags=["Analysis"])
async def get_summary(id: str):
    """
    Returns the executive and detailed summaries for the paper.
    """
    return SummaryResponse(
        executive=(
            "This study introduces a Hybrid Quantum-Classical Neural Network (HQCNN) to address the multi-echelon "
            "inventory optimization problem in supply chains under severe demand uncertainty. By combining classical "
            "deep reinforcement learning with parameterized quantum circuits, the framework successfully mitigates the "
            "curse of dimensionality, offering a 15% reduction in total operational costs and 40% faster training "
            "convergence than classical counterparts on noisy, high-dimensional supply chain data."
        ),
        detailed=(
            "Optimizing multi-echelon inventory systems requires managing complex, non-linear dependencies across "
            "supplier, manufacturer, distributor, and retailer nodes. Classical reinforcement learning models (like DQN) "
            "degrade in performance when dealing with high-dimensional state spaces and volatile demand. This research "
            "introduces a hybrid quantum-classical architecture (HQCNN) where the high-dimensional state representation "
            "is mapped onto a quantum register using amplitude encoding. Optimization is performed via parameterized "
            "quantum circuits (PQCs) with classical optimization of gate parameters. The approach was evaluated on a "
            "simulated multi-echelon automotive supply chain under non-Gaussian demand distributions. Results indicate "
            "that the quantum-enhanced model achieves a tighter safety-stock bound and converges to the global minimum "
            "with significantly fewer training iterations. However, practical implementation remains constrained by the "
            "gate errors and limited qubit counts of current NISQ-era quantum hardware, necessitating hybrid architectures "
            "that delegate heavy simulation tasks back to classical co-processors."
        )
    )

@app.get("/paper/{id}/claims", response_model=ClaimsResponse, tags=["Analysis"])
async def get_claims(id: str):
    """
    Returns a list of key claims extracted from the paper along with evidence, citations, and confidence scores.
    """
    claims = [
        ClaimEvidence(
            claim="HQCNN converges 40% faster during training than classical Deep Q-Networks (DQN).",
            evidence="We demonstrate that HQCNN converges 40% faster and exhibits a 15% reduction in total holding and stockout costs compared to classical deep Q-networks (DQN) in noisy, high-uncertainty regimes.",
            citation=CITATION_2,
            confidence=0.95
        ),
        ClaimEvidence(
            claim="The proposed method reduces total inventory holding and stockout costs by 15%.",
            evidence="We demonstrate that HQCNN converges 40% faster and exhibits a 15% reduction in total holding and stockout costs compared to classical deep Q-networks (DQN) in noisy, high-uncertainty regimes.",
            citation=CITATION_2,
            confidence=0.92
        ),
        ClaimEvidence(
            claim="Amplitude encoding provides logarithmic scaling for state representation in multi-echelon supply networks.",
            evidence="By leveraging amplitude encoding, a supply chain state containing N variables can be mapped onto log2(N) qubits, drastically reducing representation space size.",
            citation=CITATION_3,
            confidence=0.88
        )
    ]
    return ClaimsResponse(claims)

@app.get("/paper/{id}/limitations", response_model=LimitationsResponse, tags=["Analysis"])
async def get_limitations(id: str):
    """
    Returns the key limitations identified within the paper along with citations.
    """
    limitations = [
        Limitation(
            limitation="Vulnerability to quantum gate errors and decoherence in current NISQ-era hardware.",
            citation=CITATION_4
        ),
        Limitation(
            limitation="Qubit scale constraints requiring classical partitioning of large multi-echelon supply graphs.",
            citation=CITATION_5
        )
    ]
    return LimitationsResponse(limitations)

@app.get("/paper/{id}/flashcards", response_model=FlashcardsResponse, tags=["Study"])
async def get_flashcards(id: str):
    """
    Returns a set of flashcards for study purposes.
    """
    flashcards = [
        Flashcard(
            question="What is the core optimization model proposed in the paper?",
            answer="A Hybrid Quantum-Classical Neural Network (HQCNN) utilizing parameterized quantum circuits (PQCs).",
            difficulty="Medium"
        ),
        Flashcard(
            question="By what percentage does the HQCNN model reduce inventory costs compared to DQN?",
            answer="It reduces holding and stockout costs by 15% in high-uncertainty environments.",
            difficulty="Easy"
        ),
        Flashcard(
            question="How does amplitude encoding reduce qubit requirements?",
            answer="It maps a state with N variables onto log2(N) qubits, resulting in logarithmic qubit scaling.",
            difficulty="Hard"
        ),
        Flashcard(
            question="What quantum computing era is the model designed for, and what are its key bottlenecks?",
            answer="The NISQ (Noisy Intermediate-Scale Quantum) era. The key bottlenecks are gate errors, decoherence times, and limited qubit counts.",
            difficulty="Medium"
        )
    ]
    return FlashcardsResponse(flashcards)

@app.get("/paper/{id}/conceptmap", response_model=ConceptMapResponse, tags=["Study"])
async def get_concept_map(id: str):
    """
    Returns the nodes and edges defining the paper's concept map.
    """
    nodes = [
        Node(id="HQCNN", label="Hybrid Quantum-Classical Neural Network"),
        Node(id="PQC", label="Parameterized Quantum Circuits"),
        Node(id="DQN", label="Deep Q-Network (Classical)"),
        Node(id="Inventory_Opt", label="Multi-Echelon Inventory Optimization"),
        Node(id="Demand_Uncertainty", label="Demand Uncertainty"),
        Node(id="NISQ_Hardware", label="NISQ-era Quantum Hardware"),
        Node(id="Amplitude_Encoding", label="Amplitude Encoding")
    ]
    
    edges = [
        Edge(source="HQCNN", target="PQC", label="utilizes"),
        Edge(source="HQCNN", target="Amplitude_Encoding", label="uses"),
        Edge(source="HQCNN", target="Inventory_Opt", label="applies to"),
        Edge(source="Inventory_Opt", target="Demand_Uncertainty", label="addresses"),
        Edge(source="HQCNN", target="DQN", label="outperforms"),
        Edge(source="HQCNN", target="NISQ_Hardware", label="limited by")
    ]
    
    return ConceptMapResponse(nodes=nodes, edges=edges)

@app.get("/paper/{id}/brief", response_model=BriefResponse, tags=["Analysis"])
async def get_brief(id: str):
    """
    Returns a highly structured academic brief of the paper.
    """
    return BriefResponse(
        problem="Classical multi-echelon inventory optimization suffers from the curse of dimensionality when coping with volatile, non-Gaussian demand across supply chain nodes.",
        method="Proposed a Hybrid Quantum-Classical Neural Network (HQCNN) using parameterized quantum circuits (PQCs) and amplitude encoding to map supply chain states into quantum states.",
        dataset="Simulated global automotive supply chain dataset representing multi-echelon inventory transactions under demand volatility.",
        results="The proposed model converged 40% faster during training and reduced total holding and stockout costs by 15% compared to classical Deep Q-Networks (DQN).",
        limitations="Current NISQ-era hardware limitations, such as low physical qubit count, high gate error rates, and short qubit coherence times.",
        future_work="Investigate quantum error correction techniques and implement multi-agent hybrid systems for decentralized supply networks.",
        contribution="Successfully demonstrated the feasibility and cost-efficiency of using parameterized quantum circuits for complex, high-dimensional inventory decisions on near-term quantum hardware."
    )
