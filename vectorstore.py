"""
Embed corpus chunks and store in ChromaDB.
Run once to build the index; subsequent calls skip re-embedding.
"""
import chromadb
from chromadb.utils import embedding_functions
from ingest import build_corpus

CHROMA_PATH = ".chroma_db"
COLLECTION_NAME = "iui_unofficial_guide"
EMBED_MODEL = "all-MiniLM-L6-v2"


def get_collection(rebuild: bool = False):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        if rebuild:
            client.delete_collection(COLLECTION_NAME)
        else:
            return client.get_collection(name=COLLECTION_NAME, embedding_function=ef)

    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=ef)
    corpus = build_corpus()

    batch_size = 100
    for i in range(0, len(corpus), batch_size):
        batch = corpus[i:i + batch_size]
        collection.add(
            ids=[c["chunk_id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[{"filename": c["filename"], "source_url": c["source_url"]} for c in batch],
        )

    print(f"Indexed {len(corpus)} chunks into ChromaDB.")
    return collection


def search(query: str, top_k: int = 5, collection=None):
    if collection is None:
        collection = get_collection()
    results = collection.query(query_texts=[query], n_results=top_k)
    chunks = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        chunks.append({"text": doc, "filename": meta["filename"], "source_url": meta["source_url"]})
    return chunks


if __name__ == "__main__":
    col = get_collection(rebuild=True)
    hits = search("Is Yuni Xia a good professor?", collection=col)
    for h in hits:
        print(f"\n[{h['filename']}]\n{h['text'][:200]}")
