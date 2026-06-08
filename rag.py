"""
Grounded response generation using Groq + retrieved chunks.
"""
import os
from groq import Groq
from dotenv import load_dotenv
from vectorstore import search, get_collection

load_dotenv()

LLM_MODEL = "llama-3.1-8b-instant"
TOP_K = 5

SYSTEM_PROMPT = """You are a helpful advisor for students at Indiana University Indianapolis (IUI).
Answer ONLY using the information provided in the context chunks below.
Do not use any general knowledge or make up information.
If the context does not contain enough information to answer, say: "The retrieved documents don't cover this — I can only answer from collected reviews."

After your answer, always list the sources you drew from under a "Sources:" heading,
using the filename and URL provided for each chunk."""


def build_context(chunks: list[dict]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(f"[Chunk {i} — {c['filename']} | {c['source_url']}]\n{c['text']}")
    return "\n\n".join(parts)


def answer(query: str, collection=None, top_k: int = TOP_K) -> dict:
    """
    Retrieve top_k chunks, then generate a grounded answer.
    Returns dict with keys: query, answer, sources, chunks.
    """
    chunks = search(query, top_k=top_k, collection=collection)
    context = build_context(chunks)

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
        temperature=0.2,
        max_tokens=600,
    )

    answer_text = response.choices[0].message.content.strip()
    sources = list({(c["filename"], c["source_url"]) for c in chunks})

    return {
        "query": query,
        "answer": answer_text,
        "sources": sources,
        "chunks": chunks,
    }


if __name__ == "__main__":
    col = get_collection()
    result = answer("Is Yuni Xia a good professor for discrete math?", collection=col)
    print(result["answer"])
