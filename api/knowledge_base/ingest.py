#!/usr/bin/env python3
"""
Ingest PDF guidelines into ChromaDB for RAG retrieval.
Chunks PDFs by ~500 tokens with 50-token overlap.
Uses sentence-transformers for embeddings.
"""

import os
import sys
import fitz  # PyMuPDF
import chromadb
from chromadb.utils import embedding_functions

PDF_DIR = os.path.join(os.path.dirname(__file__), "pdfs")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "dementia_care_guidelines"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, 384-dim, good for retrieval
CHUNK_SIZE = 500  # ~500 tokens ≈ ~2000 chars
CHUNK_OVERLAP = 50  # ~50 tokens ≈ ~200 chars
CHARS_PER_CHUNK = 2000
CHARS_OVERLAP = 200

# Source metadata for each PDF
PDF_METADATA = {
    "apa-dementia-guidelines.pdf": {
        "source": "APA",
        "title": "APA Guidelines for the Evaluation of Dementia and Age-Related Cognitive Change",
        "year": "2021",
    },
    "nice-ng97-dementia.pdf": {
        "source": "NICE",
        "title": "NG97: Dementia Assessment, Management and Support",
        "year": "2018",
    },
    "cms-guide-model.pdf": {
        "source": "CMS",
        "title": "GUIDE Model Request for Applications",
        "year": "2024",
    },
    "cms-appendix-pp-ltcf.pdf": {
        "source": "CMS",
        "title": "State Operations Manual Appendix PP - Nursing Home Survey Guidelines",
        "year": "2024",
    },
    "cms-ftag-list.pdf": {
        "source": "CMS",
        "title": "Federal Regulatory Groups - F-Tag List",
        "year": "2024",
    },
    "alz-care-practice-recommendations.pdf": {
        "source": "Alzheimer's Association",
        "title": "Dementia Care Practice Recommendations",
        "year": "2024",
    },
    "alz-assisted-living-recommendations.pdf": {
        "source": "Alzheimer's Association",
        "title": "Dementia Care Practice Recommendations for Assisted Living",
        "year": "2024",
    },
    "alz-clinical-guidelines-2024.pdf": {
        "source": "Alzheimer's Association",
        "title": "Alzheimer's Clinical Guidelines 2024",
        "year": "2024",
    },
}


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """Extract text from PDF, returning list of {page, text}."""
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            pages.append({"page": i + 1, "text": text})
    doc.close()
    return pages


def chunk_text(pages: list[dict], filename: str) -> list[dict]:
    """Split page texts into overlapping chunks with metadata."""
    # Concatenate all pages with page markers
    full_text = ""
    page_boundaries = []  # (char_offset, page_num)
    for p in pages:
        page_boundaries.append((len(full_text), p["page"]))
        full_text += p["text"] + "\n\n"

    chunks = []
    start = 0
    chunk_id = 0

    while start < len(full_text):
        end = start + CHARS_PER_CHUNK

        # Try to break at sentence boundary
        if end < len(full_text):
            # Look for sentence end within last 200 chars of chunk
            search_start = max(end - 200, start)
            last_period = full_text.rfind(". ", search_start, end + 100)
            if last_period > search_start:
                end = last_period + 1

        chunk_text_content = full_text[start:end].strip()
        if not chunk_text_content or len(chunk_text_content) < 50:
            start = end - CHARS_OVERLAP
            continue

        # Determine which page(s) this chunk spans
        chunk_pages = []
        for offset, page_num in page_boundaries:
            if offset <= start < offset + len(full_text):
                if start <= offset <= end or offset <= start:
                    chunk_pages.append(page_num)
        # Simplify: find the page for the start position
        page_num = 1
        for offset, pn in page_boundaries:
            if offset <= start:
                page_num = pn

        meta = PDF_METADATA.get(filename, {"source": "Unknown", "title": filename, "year": "Unknown"})
        chunks.append({
            "id": f"{filename}::chunk_{chunk_id}",
            "text": chunk_text_content,
            "metadata": {
                "source": meta["source"],
                "title": meta["title"],
                "year": meta["year"],
                "filename": filename,
                "page": page_num,
                "chunk_id": chunk_id,
            },
        })
        chunk_id += 1
        start = end - CHARS_OVERLAP

    return chunks


def main():
    print(f"=== Memowell RAG Knowledge Base Ingestion ===")
    print(f"PDF directory: {PDF_DIR}")
    print(f"ChromaDB directory: {CHROMA_DIR}")
    print()

    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    # Delete existing collection if exists (fresh ingest)
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"Created collection '{COLLECTION_NAME}' with {EMBEDDING_MODEL} embeddings")
    print()

    # Process each PDF
    all_chunks = []
    for filename in sorted(os.listdir(PDF_DIR)):
        if not filename.endswith(".pdf"):
            continue
        filepath = os.path.join(PDF_DIR, filename)
        print(f"Processing: {filename}")

        pages = extract_text_from_pdf(filepath)
        print(f"  Pages extracted: {len(pages)}")

        chunks = chunk_text(pages, filename)
        print(f"  Chunks created: {len(chunks)}")
        all_chunks.extend(chunks)

    print(f"\nTotal chunks: {len(all_chunks)}")
    print(f"Embedding and storing...")

    # Batch insert (ChromaDB handles batching internally, but limit to 500 per call)
    BATCH_SIZE = 100
    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch = all_chunks[i : i + BATCH_SIZE]
        collection.add(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[c["metadata"] for c in batch],
        )
        print(f"  Stored batch {i // BATCH_SIZE + 1} ({len(batch)} chunks)")

    print(f"\n✅ Done! {len(all_chunks)} chunks stored in '{COLLECTION_NAME}'")
    print(f"   ChromaDB path: {CHROMA_DIR}")

    # Quick sanity check
    print(f"\n--- Sanity Check ---")
    results = collection.query(
        query_texts=["How to manage agitation in dementia patients"],
        n_results=3,
    )
    for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        print(f"\nResult {i + 1} [{meta['source']} p.{meta['page']}]:")
        print(f"  {doc[:150]}...")


if __name__ == "__main__":
    main()
