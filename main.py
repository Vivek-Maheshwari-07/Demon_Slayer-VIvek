from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.paper import router as paper_router

app = FastAPI(
    title="EPISTEME Production API",
    description="Integrated academic research companion API.",
    version="1.0.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
