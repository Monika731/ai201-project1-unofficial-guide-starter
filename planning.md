# Project 1 Planning: The Unofficial Guide

---

## Domain

Student reviews of CS/STEM professors and general student life at Indiana University Indianapolis (IUI). This knowledge is valuable because official university sources (course catalog, professor bios) give no insight into actual teaching quality, exam difficulty, grading style, or workload. Peer-sourced reviews from RateMyProfessors, Niche, and Reddit fill that gap — but they're scattered, unstructured, and unsearchable as a unified corpus.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Niche — IUI Academics | Student reviews of academic quality | https://www.niche.com/colleges/indiana-university-indianapolis/academics/ |
| 2 | Niche — IUI Campus Life | Student reviews of campus experience | https://www.niche.com/colleges/indiana-university-indianapolis/campus-life/ |
| 3 | Niche — IUI Overall | General school reviews | https://www.niche.com/colleges/indiana-university-indianapolis/ |
| 4 | Reddit r/IUPUI — paying for college | Financial concerns thread | https://www.reddit.com/r/IUPUI/ |
| 5 | Reddit r/IUPUI — electives | Course recommendation thread | https://www.reddit.com/r/IUPUI/ |
| 6 | RateMyProfessors — CS Dept | Reviews of Hasan, Gersting, Hill | https://www.ratemyprofessors.com |
| 7 | RateMyProfessors — Engineering | Engineering professor reviews | https://www.ratemyprofessors.com |
| 8 | RateMyProfessors — IUI School | School-level reviews | https://www.ratemyprofessors.com |
| 9 | RateMyProfessors — Math Dept | Math professor reviews | https://www.ratemyprofessors.com |
| 10 | RateMyProfessors — Yuni Xia | Focused reviews for one CS professor | https://www.ratemyprofessors.com/professor/1307154 |

---

## Chunking Strategy

**Chunk size:** 300 characters

**Overlap:** 50 characters

**Reasoning:**
The documents are student reviews — short, single-perspective entries averaging 100–250 characters each. A 300-character chunk captures 1–2 complete reviews, preserving each student's full opinion as a single unit. Larger chunks (500+) would merge opinions from multiple students, losing individual attribution and blending contradictory sentiments (e.g., one student says "best professor" immediately followed by another saying "avoid this class"). The 50-character overlap preserves the tail of the previous chunk so a thought that ends near a boundary doesn't lose its final clause entirely.

We split on sentence endings (`[.!?] `) first, then fall back to hard character splits only when a single sentence exceeds 300 characters (rare in this corpus).

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

**Top-k:** 5

**Production tradeoff reflection:**
`all-MiniLM-L6-v2` is free, local, and fast — ideal for a student project or small deployment. In production I would weigh:

- **Context length**: This model maxes at 256 tokens. If we expand to richer documents (syllabi, department handbooks), we'd need `nomic-embed-text` or `text-embedding-3-small` (both support 8k tokens).
- **Accuracy**: A model fine-tuned on educational reviews would outperform on domain-specific slang and abbreviations ("DCS", "CSCI 23000", professor nicknames).
- **Cost vs. local**: OpenAI embeddings (~$0.02/million tokens) are simple to integrate but add latency and API dependency. Local models trade setup complexity for zero marginal cost.
- **Multilingual**: IUI has a large international student population. A multilingual model (`multilingual-e5-large`) would handle reviews in Spanish, Hindi, or Mandarin — something `all-MiniLM-L6-v2` cannot.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Is Yuni Xia a good professor for discrete math? | Yes — students say she curves heavily, lectures are clear, and homework is light. Manageable class if you attend. |
| 2 | What do students say about Mohammad Hasan's CS class? | Strongly negative — frequently unprepared, surprise quizzes, very hard exams, projects unclear. |
| 3 | What are students' biggest concerns about paying for college at IUI? | High housing/living costs (~$1,500/month), need to work 25–30 hrs/week, reliance on loans and FAFSA. |
| 4 | What electives do IUI CS students recommend? | Reddit thread recommends CSCI 23000 (intro Python, easy online course) for students outside CS. |
| 5 | How is campus life at IUI compared to a traditional college experience? | IUI is a commuter campus — most students don't live on campus, fewer organized social activities, more urban/professional feel. |

---

## Anticipated Challenges

1. **Flat file structure of scraped documents**: All source files have no newlines — reviews are concatenated into one long string. Chunking strategies that rely on paragraph breaks or line endings will fail silently, producing either one massive chunk or no chunks at all. Mitigation: use sentence-boundary splitting rather than newline-based splitting.

2. **Short chunks losing cross-sentence context for Q&A documents**: Reddit threads have a question followed by multiple replies. If the question and replies land in different chunks, retrieval may find the question-chunk but miss the answer-chunks, and the model will report insufficient context even though the answer exists. Mitigation: increase top_k or consider chunking Reddit files as whole Q+reply groups.

---

## Architecture

```
documents/*.txt
       │
       ▼
  [Ingestion — ingest.py]
  load_documents() → clean_text() → chunk_text()
       │
       ▼ list of {chunk_id, filename, source_url, text}
       │
  [Embedding + Vector Store — vectorstore.py]
  SentenceTransformer("all-MiniLM-L6-v2")
  ChromaDB (persistent, .chroma_db/)
       │
       ▼ on query:
  [Retrieval — vectorstore.search()]
  top-5 semantically similar chunks
       │
       ▼
  [Generation — rag.py]
  Groq API (llama-3.1-8b-instant)
  grounded system prompt + retrieved context
       │
       ▼
  [Interface — app.py]
  Streamlit web UI
  shows answer + expandable chunk panel with sources
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
I will give Claude the list of document filenames, their raw content structure (flat strings, SOURCE: header format), and the chunking strategy spec above. I will ask it to implement `load_documents()`, `clean_text()`, and `chunk_text()` in `ingest.py` matching exactly the chunk size, overlap, and sentence-boundary strategy described. I will verify by running `python ingest.py` and checking that the total chunk count is reasonable and that no chunk is empty or exceeds 350 characters.

**Milestone 4 — Embedding and retrieval:**
I will give Claude the `ingest.py` output schema (`{chunk_id, filename, source_url, text}`) and the retrieval approach spec above, and ask it to implement `vectorstore.py` using ChromaDB's `SentenceTransformerEmbeddingFunction`. I will verify by running a test query and confirming the top-5 results are from relevant documents.

**Milestone 5 — Generation and interface:**
I will give Claude the system prompt grounding instruction above and ask it to implement `rag.py` (retrieves + calls Groq) and a Streamlit `app.py` with a text input, answer display, and expandable source panel. I will verify by running the 5 evaluation questions manually in the UI and checking that sources are cited.
