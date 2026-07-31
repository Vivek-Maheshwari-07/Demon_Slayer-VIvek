import os
import sys
import requests
import fitz  # PyMuPDF

BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8000")
DUMMY_PDF_PATH = "dummy_test.pdf"

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def create_dummy_pdf() -> bool:
    """Generates a small valid PDF file on the fly with text contents."""
    try:
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text(
            (72, 72),
            "EPISTEME System Verification Document.\n"
            "This paper introduces the parallel workflow for fast RAG operations.\n"
            "We demonstrate a spatial chunking method that retains page numbers to enforce grounding.\n"
            "Our empirical evaluation yields 98% factual precision on scientific benchmark sets."
        )
        doc.save(DUMMY_PDF_PATH)
        doc.close()
        return True
    except Exception as e:
        print(f"Error compiling dummy PDF: {e}")
        return False


def print_result(test_name: str, success: bool, error_msg: str = ""):
    if success:
        print(f"[{GREEN}PASS{RESET}] - {test_name}")
    else:
        print(f"[{RED}FAIL{RESET}] - {test_name} | Error: {error_msg}")


def main():
    print("=" * 60)
    print("EPISTEME Integration & API Sanity Verification")
    print("=" * 60)

    if not create_dummy_pdf():
        print(f"[{RED}FAIL{RESET}] - Failed to set up dummy PDF file. Aborting.")
        sys.exit(1)

    paper_id = None

    try:
        # 1. Health Check
        try:
            res = requests.get(f"{BASE_URL}/")
            print_result("FastAPI Health Check (GET /)", res.status_code == 200)
        except Exception as e:
            print_result("FastAPI Health Check (GET /)", False, f"Connection refused. Is server running on {BASE_URL}?")
            sys.exit(1)

        # 2. Upload Ingestion
        try:
            with open(DUMMY_PDF_PATH, "rb") as f:
                res = requests.post(f"{BASE_URL}/upload", files={"file": f})
            if res.status_code == 200:
                paper_id = res.json().get("paper_id")
                print_result(f"Upload Ingestion (POST /upload) [ID: {paper_id}]", True)
            else:
                print_result("Upload Ingestion (POST /upload)", False, f"Status: {res.status_code} - {res.text}")
        except Exception as e:
            print_result("Upload Ingestion (POST /upload)", False, str(e))

        if not paper_id:
            print(f"[{RED}FAIL{RESET}] - No paper_id retrieved. Skipping subsequent checks.")
            sys.exit(1)

        # 3. Retrieve Metadata
        try:
            res = requests.get(f"{BASE_URL}/paper/{paper_id}/metadata")
            print_result("Metadata Extraction (GET /paper/{id}/metadata)", res.status_code == 200)
        except Exception as e:
            print_result("Metadata Extraction (GET /paper/{id}/metadata)", False, str(e))

        # 4. Extract Claims
        try:
            res = requests.post(f"{BASE_URL}/paper/{paper_id}/claims")
            print_result("CoVe Claims Verification (POST /paper/{id}/claims)", res.status_code == 200)
        except Exception as e:
            print_result("CoVe Claims Verification (POST /paper/{id}/claims)", False, str(e))

        # 5. Grounding Q&A Engine
        try:
            payload = {"question": "What is the factual precision score mentioned in the evaluation?"}
            res = requests.post(f"{BASE_URL}/paper/{paper_id}/ask", json=payload)
            print_result("Grounding Q&A Engine (POST /paper/{id}/ask)", res.status_code == 200)
        except Exception as e:
            print_result("Grounding Q&A Engine (POST /paper/{id}/ask)", False, str(e))

    finally:
        if os.path.exists(DUMMY_PDF_PATH):
            os.remove(DUMMY_PDF_PATH)

    print("=" * 60)


if __name__ == "__main__":
    main()
