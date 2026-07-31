import re
import uuid
import fitz  # PyMuPDF
from typing import List, Dict, Any

def split_into_sentences(text: str) -> List[str]:
    """
    Splits text into sentences using a regex pattern that handles common abbreviations.
    """
    # Negative lookbehinds prevent splitting on e.g., i.e., Dr., Prof., et al., etc.
    sentence_end = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<!et al\.)(?<=\.|\?|!)\s')
    sentences = sentence_end.split(text)
    return [s.strip() for s in sentences if s.strip()]

def extract_text_with_pages(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Opens the PDF and extracts all text blocks, mapping each sentence to its corresponding page number.
    Uses 1-based page indexing.
    """
    sentence_data = []
    
    # Open PDF document
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        # Get blocks of text from page
        blocks = page.get_text("blocks")
        for block in blocks:
            # block structure: (x0, y0, x1, y1, text, block_no, block_type)
            # block_type 0 is text, 1 is image
            if block[6] == 0:
                text = block[4].replace('\n', ' ').strip()
                if not text:
                    continue
                sentences = split_into_sentences(text)
                for sentence in sentences:
                    sentence_data.append({
                        "text": sentence,
                        "page": page_num + 1  # 1-indexed page number
                    })
                    
    doc.close()
    return sentence_data

def chunk_text(sentence_data: List[Dict[str, Any]], target_words: int = 350) -> List[Dict[str, Any]]:
    """
    Groups individual sentences into semantic chunks of approximately target_words (~400-500 tokens).
    Assigns each chunk a unique uuid4 ID and records all page numbers touched by the chunk.
    """
    chunks = []
    current_chunk_sentences = []
    current_word_count = 0
    current_pages = []

    for item in sentence_data:
        words = item["text"].split()
        word_count = len(words)
        if not words:
            continue
        
        page_num = item["page"]
            
        # Check if adding this sentence would exceed the target word count
        # (Only split if we already have some sentences in the current chunk)
        if current_word_count > 0 and (current_word_count + word_count) > target_words:
            chunk_text_str = " ".join(current_chunk_sentences)
            sorted_pages = sorted(list(set(current_pages)))
            start_page = sorted_pages[0] if sorted_pages else 1
            page_display = f"{sorted_pages[0]}-{sorted_pages[-1]}" if len(sorted_pages) > 1 else str(start_page)
            pages_str = ",".join(str(p) for p in sorted_pages)

            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "text": chunk_text_str,
                "metadata": {
                    "page": start_page,
                    "pages": pages_str,
                    "page_display": page_display
                }
            })
            # Reset trackers for next chunk
            current_chunk_sentences = [item["text"]]
            current_word_count = word_count
            current_pages = [page_num]
        else:
            current_chunk_sentences.append(item["text"])
            current_word_count += word_count
            if page_num not in current_pages:
                current_pages.append(page_num)

    # Append any trailing sentences in the last chunk
    if current_chunk_sentences:
        chunk_text_str = " ".join(current_chunk_sentences)
        sorted_pages = sorted(list(set(current_pages)))
        start_page = sorted_pages[0] if sorted_pages else 1
        page_display = f"{sorted_pages[0]}-{sorted_pages[-1]}" if len(sorted_pages) > 1 else str(start_page)
        pages_str = ",".join(str(p) for p in sorted_pages)

        chunks.append({
            "chunk_id": str(uuid.uuid4()),
            "text": chunk_text_str,
            "metadata": {
                "page": start_page,
                "pages": pages_str,
                "page_display": page_display
            }
        })

    return chunks

def ingest_pdf(pdf_path: str, target_words: int = 350) -> List[Dict[str, Any]]:
    """
    High-level function to ingest a PDF file, parse its pages, 
    and output a list of semantic chunks with page metadata.
    """
    sentence_data = extract_text_with_pages(pdf_path)
    return chunk_text(sentence_data, target_words=target_words)

# Alias for ingestion integration
parse_pdf = ingest_pdf
