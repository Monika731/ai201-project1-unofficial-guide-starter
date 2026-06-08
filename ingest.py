"""
Document ingestion pipeline.
Loads raw .txt files, cleans them, and chunks into overlapping segments.
"""
import os
import re

DOCUMENTS_DIR = "documents"
CHUNK_SIZE = 300   # characters — short reviews fit well in this window
CHUNK_OVERLAP = 50  # characters of overlap to avoid cutting across a thought


def load_documents(doc_dir: str = DOCUMENTS_DIR) -> list[dict]:
    """Load all .txt files and return list of {filename, source_url, text} dicts."""
    docs = []
    for fname in sorted(os.listdir(doc_dir)):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(doc_dir, fname)
        with open(path, encoding="utf-8", errors="replace") as f:
            raw = f.read()
        source_url, text = _extract_source(raw)
        docs.append({"filename": fname, "source_url": source_url, "text": text})
    return docs


def _extract_source(raw: str) -> tuple[str, str]:
    """Pull SOURCE: url from first line, return (url, remaining text)."""
    match = re.match(r"SOURCE:\s*(\S+)\s+DATE_COLLECTED:[^\n]*", raw)
    if match:
        url = match.group(1)
        text = raw[match.end():]
    else:
        url = "unknown"
        text = raw
    return url, text


def clean_text(text: str) -> str:
    """
    Light cleanup for raw scraped review text:
    - Normalize whitespace / line endings
    - Remove replacement characters from encoding issues
    - Collapse repeated dashes (separator artifacts from scraping)
    - Strip leading/trailing whitespace
    """
    text = text.replace("�", " ")          # encoding replacement chars
    text = re.sub(r"-{3,}", " ", text)          # --- separator lines
    text = re.sub(r"\s+", " ", text)            # collapse whitespace
    return text.strip()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping character-level windows.
    We prefer splitting at sentence boundaries where possible.
    """
    # Try to split on sentence endings first so chunks are more self-contained
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= chunk_size:
            current = (current + " " + sentence).strip()
        else:
            if current:
                chunks.append(current)
            # If single sentence is longer than chunk_size, hard-split it
            while len(sentence) > chunk_size:
                chunks.append(sentence[:chunk_size])
                sentence = sentence[max(0, chunk_size - overlap):]
            current = sentence

    if current:
        chunks.append(current)

    # Apply overlap: prefix each chunk (except first) with end of previous chunk
    overlapped = []
    for i, chunk in enumerate(chunks):
        if i > 0 and overlap > 0:
            prefix = chunks[i - 1][-overlap:]
            chunk = (prefix + " " + chunk).strip()
        overlapped.append(chunk)

    return overlapped


def build_corpus(doc_dir: str = DOCUMENTS_DIR) -> list[dict]:
    """
    Full pipeline: load → clean → chunk.
    Returns list of chunk dicts: {chunk_id, filename, source_url, text}.
    """
    docs = load_documents(doc_dir)
    corpus = []
    for doc in docs:
        cleaned = clean_text(doc["text"])
        chunks = chunk_text(cleaned)
        for idx, chunk in enumerate(chunks):
            corpus.append({
                "chunk_id": f"{doc['filename']}__chunk{idx:03d}",
                "filename": doc["filename"],
                "source_url": doc["source_url"],
                "text": chunk,
            })
    return corpus


if __name__ == "__main__":
    corpus = build_corpus()
    print(f"Total chunks: {len(corpus)}")
    for c in corpus[:3]:
        print(f"\n[{c['chunk_id']}]\n{c['text'][:200]}")
