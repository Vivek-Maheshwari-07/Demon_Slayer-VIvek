import os
import re
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class VectorStore:
    def __init__(self, persist_dir: str = "./storage/chroma"):
        """
        Initializes the VectorStore, configuring the local directory for ChromaDB
        and loading the sentence-transformers BGE model.
        """
        # Ensure the persistent storage directory exists
        os.makedirs(persist_dir, exist_ok=True)
        
        # Initialize the persistent client
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Load the BGE model for local CPU/GPU execution
        self.model = SentenceTransformer("BAAI/bge-small-en-v1.5")

    def _get_collection_name(self, paper_id: str) -> str:
        """
        Helper method to sanitize paper_id into a valid ChromaDB collection name:
        - 3-63 characters long
        - starts/ends with alphanumeric
        - contains only lowercase alphanumeric, dots, dashes, underscores
        """
        cleaned = paper_id.lower().strip()
        # Replace invalid characters with a hyphen
        cleaned = re.sub(r'[^a-z0-9\._-]', '-', cleaned)
        # Ensure it starts with alphanumeric
        cleaned = re.sub(r'^[^a-z0-9]+', 'p', cleaned)
        # Ensure it ends with alphanumeric
        cleaned = re.sub(r'[^a-z0-9]+$', '0', cleaned)
        
        # Ensure length matches Chroma constraints (3-63 chars)
        if len(cleaned) < 3:
            cleaned = cleaned.ljust(3, '0')
        elif len(cleaned) > 63:
            cleaned = cleaned[:63]
            # Ensure it still ends with an alphanumeric char after truncation
            cleaned = re.sub(r'[^a-z0-9]+$', '0', cleaned)
            
        return cleaned

    def add_paper(self, paper_id: str, chunks: List[Dict[str, Any]]) -> None:
        """
        Gets or creates a ChromaDB collection for the given paper_id, 
        encodes the text chunks, and upserts them into ChromaDB.
        """
        collection_name = self._get_collection_name(paper_id)
        collection = self.client.get_or_create_collection(name=collection_name)
        
        if not chunks:
            return

        ids = [chunk["chunk_id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        # Generate 384-dimensional embeddings (BGE-small-en-v1.5)
        # Pass document texts directly (no query prefix required for indexing)
        embeddings = self.model.encode(documents, show_progress_bar=False).tolist()
        
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, paper_id: str, query: str, top_k: int = 6) -> List[Dict[str, Any]]:
        """
        Queries ChromaDB for the most relevant document chunks matching the query.
        Uses the BGE query prefix for asymmetric retrieval.
        """
        collection_name = self._get_collection_name(paper_id)
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            # Collection doesn't exist yet, return an empty list of results
            return []

        # BGE models require an instruction prefix for query embeddings
        prefixed_query = f"Represent this sentence for searching relevant passages: {query}"
        
        # Encode the query
        query_embedding = self.model.encode(prefixed_query, show_progress_bar=False).tolist()
        
        # Query the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        formatted_results = []
        if results and "documents" in results and results["documents"]:
            # Retrieve lists (n_results lists inside query_embeddings list)
            documents = results["documents"][0]
            ids = results["ids"][0]
            metadatas = results["metadatas"][0]
            
            for idx in range(len(documents)):
                meta = metadatas[idx] if metadatas and idx < len(metadatas) else {}
                page = meta.get("page", 1) if meta else 1
                page_display = meta.get("page_display", str(page)) if meta else str(page)
                formatted_results.append({
                    "chunk_id": ids[idx],
                    "text": documents[idx],
                    "page": page,
                    "page_display": page_display
                })
                
        return formatted_results
