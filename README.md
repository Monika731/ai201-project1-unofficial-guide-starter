# The Unofficial Guide — IUI CS/STEM Professor Reviews

---

## Domain

Student reviews and experiences for CS/STEM professors and general student life at Indiana University Indianapolis (IUI, formerly IUPUI). This knowledge is valuable because official course descriptions and university websites tell you nothing about a professor's actual teaching style, grading difficulty, workload, or whether their exams match the material they teach. Students planning their course schedule need peer intelligence — "should I take Yuni Xia for discrete math?" — that official channels simply don't surface.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Niche — IUI Academics reviews | Scraped reviews | https://www.niche.com/colleges/indiana-university-indianapolis/academics/ |
| 2 | Niche — IUI Campus Life reviews | Scraped reviews | https://www.niche.com/colleges/indiana-university-indianapolis/campus-life/ |
| 3 | Niche — IUI Overall reviews | Scraped reviews | https://www.niche.com/colleges/indiana-university-indianapolis/ |
| 4 | Reddit r/IUPUI — paying for college thread | Forum discussion | https://www.reddit.com/r/IUPUI/ |
| 5 | Reddit r/IUPUI — electives advice thread | Forum discussion | https://www.reddit.com/r/IUPUI/ |
| 6 | RateMyProfessors — CS Department (Hasan, Gersting, Hill) | Professor reviews | https://www.ratemyprofessors.com |
| 7 | RateMyProfessors — Engineering Department | Professor reviews | https://www.ratemyprofessors.com |
| 8 | RateMyProfessors — IUI School Reviews | School-level reviews | https://www.ratemyprofessors.com |
| 9 | RateMyProfessors — Math Department | Professor reviews | https://www.ratemyprofessors.com |
| 10 | RateMyProfessors — Prof. Yuni Xia (CS) | Professor reviews | https://www.ratemyprofessors.com/professor/1307154 |

---

## Ingestion Pipeline

**How it works (`ingest.py`):**

1. **Load** — every `.txt` file in `documents/` is read; the `SOURCE:` URL and `DATE_COLLECTED:` header are extracted from the first line using a regex and stored as metadata.
2. **Clean** — `clean_text()` strips UTF-8 replacement characters, collapses repeated dash separators (artifacts from copy-paste scraping), and normalizes all whitespace to single spaces. This matters because the raw files have no newlines — the entire document is one long string of concatenated reviews.
3. **Chunk** — `chunk_text()` first splits on sentence boundaries (`[.!?] `) so each chunk is a semantically coherent unit, then applies a 50-character overlap prefix from the previous chunk.
4. **Output** — each chunk carries its `chunk_id`, `filename`, and `source_url` so attribution is preserved end-to-end.

Total chunks produced: **127** across 10 documents.

---

## Chunking Strategy

**Chunk size:** 300 characters

**Overlap:** 50 characters

**Why these choices fit your documents:**
The source documents are short, dense student reviews — not long-form essays or FAQs. A typical review is 2–4 sentences (100–250 characters). A 300-character window captures 1–2 complete reviews per chunk, keeping each chunk semantically self-contained. Using 500+ characters would merge reviews from different students into one chunk, blurring attribution and mixing sentiment. The 50-character overlap ensures that a sentence split exactly at a chunk boundary isn't completely lost — the prefix carries just enough context to tie the chunk to the prior thought.

We split on sentence endings first (rather than hard character splits) so chunks don't end mid-word or mid-thought.

**Final chunk count:** 127 chunks across 10 documents.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` (via `sentence-transformers`)

**Why:** Fast, free, runs locally with no API key, and performs well on short English text. Each review chunk is under 50 tokens — well within this model's 256-token context limit. For a student review domain in English, general-purpose semantic similarity is sufficient.

**Production tradeoff reflection:**
If deploying for real users I would weigh several alternatives:

- **Context length**: `all-MiniLM-L6-v2` maxes out at 256 tokens. For longer source documents (full course syllabi, multi-page PDFs), I'd switch to `text-embedding-3-small` (OpenAI, 8192-token limit) or `nomic-embed-text` (8192 tokens, open-weight, local). Our 300-char chunks stay under 256 tokens, so this isn't a current bottleneck.
- **Accuracy on domain text**: General models do reasonably well here because "professor," "exam," "curve," and "grading" are common English words. A fine-tuned model on educational reviews would outperform on edge cases (slang, professor nicknames, abbreviations like "DCS" or "CSCI").
- **Cost**: `all-MiniLM-L6-v2` is free and local — zero API cost. OpenAI's `text-embedding-3-small` costs ~$0.02/million tokens, which matters at scale.
- **Multilingual**: Not relevant for this English-only corpus, but international student communities (a real IUI use case) might post in other languages — `multilingual-e5-large` handles 100+ languages.
- **Latency**: Local inference is slower than an API call for large batches but has no network round-trip. For real-time query embedding, the difference is negligible (<50 ms per query).

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are a helpful advisor for students at Indiana University Indianapolis (IUI).
Answer ONLY using the information provided in the context chunks below.
Do not use any general knowledge or make up information.
If the context does not contain enough information to answer, say:
"The retrieved documents don't cover this — I can only answer from collected reviews."

After your answer, always list the sources you drew from under a "Sources:" heading,
using the filename and URL provided for each chunk.
```

**How source attribution is surfaced in the response:**
Each chunk passed to the model is prefixed with `[Chunk N — filename | source_url]`. The system prompt instructs the model to list sources at the end of every answer. The Python `answer()` function in `rag.py` also programmatically deduplicates and returns `sources` (filename + URL pairs) so the Streamlit UI can display them in an expandable "Retrieved chunks" panel independent of what the model writes.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Is Yuni Xia a good professor for discrete math? | Yes — curves heavily, helpful, manageable | Yes — cites heavy curves, good teaching, low homework | Relevant | Accurate |
| 2 | What do students say about Mohammad Hasan's CS class? | Negative — unprepared, hard exams, unclear | Mixed — mentions knowledge gain AND unpreparedness; undersells severity of negative reviews | Relevant | Partially accurate |
| 3 | What are students' biggest concerns about paying for college at IUI? | Housing costs, work/study balance, loans | "The retrieved documents don't cover this" — despite relevant content existing in the corpus | Partially relevant | Inaccurate |
| 4 | What electives do IUI CS students recommend? | Specific course suggestions from Reddit | Correctly cites CSCI 23000 from the Reddit electives thread | Relevant | Accurate |
| 5 | How is campus life at IUI compared to a traditional college? | Commuter-heavy, urban, community feel | Accurately describes commuter campus, limited on-campus life, quieter vibe | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**
Q3 — "What are students' biggest concerns about paying for college at IUI?"

**What the system returned:**
> "The retrieved documents don't cover this — I can only answer from collected reviews."

This is incorrect — `reddit_iui_class_advice.txt` contains an entire thread about housing costs ($1,000–$1,500/month), loan dependence, 25–30 hours/week of work, and public transit workarounds.

**Root cause (tied to a specific pipeline stage):**
The root cause is in the **chunking stage**. The `reddit_iui_class_advice.txt` file has no newlines — it is one continuous string. The Reddit post's *question* (about paying for college) appears near the start of the file, and the *student responses* containing actionable answers (loans, FAFSA, working on campus) are in the middle and end. After sentence-based chunking, the question lands in one chunk and the responses land in separate chunks further in the file. The embedding for "biggest concerns about paying" scores highest against the question-posing chunk — but that chunk only contains the problem framing ("housing could be $1,500/month"), not the solutions. The model receives context describing the problem but not what students actually do, so it correctly reports the context is insufficient.

**What you would change to fix it:**
Two improvements: (1) **Increase top_k** from 5 to 8–10 so more chunks from the same document are retrieved, giving the model the full thread context. (2) **Preserve Reddit thread structure** by chunking the Reddit documents as question + top replies together rather than pure sentence windows — the question and its responses are semantically inseparable and should always appear in the same chunk.

---

## Spec Reflection

**One way the spec helped you during implementation:**
Defining the 5 evaluation questions in advance forced a concrete test of the chunking strategy before writing a single line of embedding code. When Q3 failed, I could trace the failure directly back to the chunk structure documented in planning.md — the sentence-boundary split works well for review corpora but breaks for Q&A thread formats where the question and answers are in different parts of the same flat string.

**One way your implementation diverged from the spec, and why:**
The spec anticipated standard paragraph-separated documents and planned a simpler character-split chunker. In implementation, I discovered the scraped documents have zero newlines — the entire file is one continuous string. I had to switch from a newline/paragraph-based split to a sentence-boundary regex split. This worked better for the review corpus but introduced the Q3 failure case for the Reddit thread, which has a different internal structure than review documents.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The full list of required features, the existing `requirements.txt` (showing chromadb, groq, sentence-transformers), and all 10 raw document files.
- *What it produced:* Complete implementations of `ingest.py`, `vectorstore.py`, `rag.py`, `app.py`, and `evaluate.py` — a working end-to-end RAG pipeline.
- *What I changed or overrode:* The Groq model ID `llama3-8b-8192` was decommissioned; I updated it to `llama-3.1-8b-instant`. I also directed the chunk size to 300 characters (rather than a default 500) because the source documents are short reviews, not long-form text.

**Instance 2**

- *What I gave the AI:* The actual terminal output from running `evaluate.py` — all 5 question/answer pairs with real system responses and chunk filenames.
- *What it produced:* Completed evaluation table and failure case analysis grounded in observed retrieval behavior.
- *What I changed or overrode:* I verified the Q3 failure explanation against the actual document content and confirmed the relevant financial content exists in `reddit_iui_class_advice.txt` but falls into chunks that don't match the query embedding well enough to rank in the top 5.

---

## Running the System

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install streamlit

# 2. Set your Groq API key in .env
#    Get a free key at https://console.groq.com

# 3. Build the vector index (runs once, persists to .chroma_db/)
python vectorstore.py

# 4. Launch the Streamlit interface
streamlit run app.py

# 5. (Optional) Run the evaluation report
python evaluate.py
```
