import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("episteme")

api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
if not api_key:
    logger.warning("OPENROUTER_API_KEY is not configured in environment.")
else:
    logger.info("OPENROUTER_API_KEY loaded successfully.")

from routes.paper import router as paper_router, vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        vector_store.model.encode("warmup sentence for BGE model caching", show_progress_bar=False)
        logger.info("Embedding model (BAAI/bge-small-en-v1.5) warmed up successfully.")
    except Exception as e:
        logger.warning(f"Embedding model warmup failed: {e}")
    yield


app = FastAPI(
    title="EPISTEME Research API",
    description="Fact-grounded academic paper processing and research API.",
    version="1.0.0",
    lifespan=lifespan,
)

allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(paper_router)


@app.get("/")
async def root():
    return {"status": "EPISTEME API Live", "version": "1.0.0"}
