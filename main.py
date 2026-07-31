from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.paper import router as paper_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Warm up BGE embedding model
    try:
        from vector_store import VectorStore
        vs = VectorStore()
        vs.model.encode("warmup sentence for BGE model caching", show_progress_bar=False)
        print("Embedding model BAAI/bge-small-en-v1.5 successfully warmed up on startup.")
    except Exception as e:
        print(f"Warning: Embedding model warmup encountered an issue: {e}")
    yield

app = FastAPI(
    title="EPISTEME Production API",
    description="Integrated academic research companion API.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS middleware (restricted to Vite/React dev ports)
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the paper router
app.include_router(paper_router)

@app.get("/")
async def root():
    """
    Root endpoint serving as a simple health check.
    """
    return {"status": "EPISTEME API Live"}
