# Paper Exercises — Jeong (2023) RAG + LLM Study

---

## Exercise 1: Article Structure

**Section locations and purposes**

| Section | Starts at | Purpose |
|---|---|---|
| Introduction | p. 2 | Explains LLM limitations (hallucination, data gaps) and introduces RAG as the solution |
| Related Work | p. 4 | Covers generative AI background, LLM training, prompt engineering, RAG, and vector databases |
| Methods | p. 19 | Describes the RAG + LangChain implementation framework step by step |
| Experiment | p. 20 | Shows actual Python code and results for each pipeline step using real documents |
| Conclusion | p. 26 | Summarises findings, admits limitations, and suggests future research directions |

**Format:** The paper follows the **IMRaD** structure (Introduction, Methods, Results/Experiment, and Discussion/Conclusion). The "Related Work" chapter is unusually long — it takes up nearly half the paper. A dedicated "Results" section with measured outcomes is missing; the experiment chapter shows implementation screenshots but no numerical evaluation.

---

## Exercise 2: Critical Analysis of Experimental Design

| Question | Answer |
|---|---|
| Research question | Can a RAG-based LLM application overcome information scarcity and hallucination in enterprise settings? |
| Type of study | Implementation case study — no controlled experiment |
| Independent variable | The data source type (PDF, TXT, DOCX, web page, YouTube) and the model used (GPT-3.5-turbo vs. GPT4All) |
| Dependent variable | Quality and relevance of generated answers (assessed informally by the author) |
| Datasets and tools | Internal company documents (dress code PDF, payment TXT, leave DOCX); LangChain, ChromaDB, FAISS, OpenAI API, GPT4All, Google Colab |
| Control / baseline | None. There is no comparison against a model without RAG, or against fine-tuning with measured scores |
| Repeatability | Partially — code snippets are shown and tools are named, but the actual source documents are not public, so full reproduction is not possible |

---

## Exercise 3: Evaluation Metrics and Evidence

**Performance claims found in the paper**

- Fine-tuned GPT-3.5 Turbo "exhibits comparable, and in some cases superior, performance to base GPT-4 on narrow tasks" — cited from OpenAI, not measured by the author.
- RAG is described as producing "more accurate and reliable answers" — no score or metric is given.
- The cost of fine-tuning GPT-3.5 Turbo ($2.40 for 100k tokens over 3 epochs) is mentioned as a reason to prefer RAG.

**Evaluation metrics used:** None. The paper shows screenshots of chatbot answers and judges them qualitatively.

**Are these metrics appropriate?** No. For a system that claims to reduce hallucination and improve accuracy, qualitative screenshots are insufficient. The task requires measurable outcomes.

**What could be added to strengthen the evidence**

- Accuracy score — compare RAG answers vs. ground-truth answers on a fixed question set
- Hallucination rate — count factually wrong answers with and without RAG
- Latency — measure response time per query
- Human evaluation — ask reviewers to rate answer relevance and correctness
- Comparison condition — run the same questions on the plain LLM (no RAG) to show the improvement

---

## Exercise 4: Cornell Notes — Section 3.2.1 RAG Based Implementation Procedure

```
┌─────────────────────────┬──────────────────────────────────────────────────────┐
│ CUE COLUMN              │ NOTES                                                │
│ (Key terms / Questions) │                                                      │
├─────────────────────────┼──────────────────────────────────────────────────────┤
│ What is chunking?       │ Splitting large documents into small text fragments  │
│                         │ (sentences or paragraphs, max 500 chars) so the      │
│                         │ vector search can find specific relevant pieces.     │
├─────────────────────────┼──────────────────────────────────────────────────────┤
│ What does embedding do? │ Converts each text chunk into a numerical vector     │
│                         │ using OpenAI or GPT4All. Similar chunks end up with  │
│                         │ similar vectors — this enables semantic search.      │
├─────────────────────────┼──────────────────────────────────────────────────────┤
│ What does ChromaDB      │ Stores all the embedding vectors. When a user asks   │
│ store?                  │ a question, Chroma finds the chunks whose vectors    │
│                         │ are closest to the question vector (cosine           │
│                         │ similarity).                                         │
├─────────────────────────┼──────────────────────────────────────────────────────┤
│ How does the LLM get    │ The top-k retrieved chunks are added into the prompt │
│ the context?            │ alongside the user's question. The LLM reads them   │
│                         │ as context and generates an answer based on that     │
│                         │ information — not just its training data.            │
├─────────────────────────┼──────────────────────────────────────────────────────┤
│ What orchestrates all   │ LangChain — it chains all the steps: loading,        │
│ the steps?              │ splitting, embedding, storing, retrieving, and       │
│                         │ calling the LLM.                                     │
└─────────────────────────┴──────────────────────────────────────────────────────┘

SUMMARY
The RAG pipeline has six steps: collect source data, split it into chunks, convert
chunks into vectors (embeddings), store vectors in ChromaDB, retrieve the most
relevant chunks for each user query using cosine similarity, and feed those chunks
plus the query into the LLM to generate a grounded answer. LangChain orchestrates
the whole flow. The key insight is that the LLM never has to "remember" the document
— it reads the relevant parts fresh each time it answers.
```

---

## Exercise 5: 5W1H Summary

| 5W1H | Answer |
|---|---|
| **Who** | Cheonsu Jeong, Principal Consultant at Samsung SDS |
| **What** | A RAG-based LLM application framework for enterprise generative AI services |
| **When / Where** | Published in 2023; Samsung SDS, Seoul, South Korea |
| **Why** | LLMs hallucinate and lack access to private or recent enterprise data; fine-tuning is expensive |
| **How** | Documents are chunked, embedded, and stored in a vector database; queries retrieve relevant chunks and pass them to the LLM as context |

**4-sentence paragraph summary**

This study set out to solve two core limitations of LLMs in business settings: hallucination and the inability to access internal or up-to-date enterprise data. The author proposed and implemented a RAG pipeline using LangChain as the orchestration framework, OpenAI embeddings, ChromaDB or FAISS as the vector store, and GPT-3.5-turbo or GPT4All as the LLM. The implementation was demonstrated across multiple document types — PDFs, Word files, plain text, web pages, and YouTube videos — with chatbot answers shown through screenshots. The practical implication is that businesses can build accurate, document-grounded chatbots without expensive model retraining, simply by connecting their existing documents to an LLM through a RAG pipeline.

---

## Exercise 6: Design Reflection — Your Own RAG Pipeline

**Use case: University Student Support Chatbot**

Students often struggle to find answers buried in course handbooks, exam regulations, and scholarship guidelines. A RAG chatbot could answer questions like "What happens if I miss an exam?" or "What are the GPA requirements for this scholarship?" instantly and accurately.

**Simplified RAG pipeline**

| Step | Decision | Reason |
|---|---|---|
| Data to collect | Course handbooks, exam rules, FAQ PDFs, scholarship documents | These are the documents students need most and they change each semester |
| Chunk size | ~400–600 characters with slight overlap | Short enough for precise retrieval, overlap prevents cutting off key sentences |
| Vector database | ChromaDB | Free, easy to set up locally, good for a small-to-medium document collection |
| LLM | GPT-3.5-turbo via API (or Mistral-7B locally for cost savings) | Good balance of quality and cost; Mistral works offline if privacy is a concern |
| Handling hallucinations | Show the source chunk alongside the answer so students can verify it | Transparency reduces trust issues; if the chunk doesn't support the answer, the student will notice |
| Handling outdated info | Re-embed documents at the start of each semester automatically | Keeps the vector store current without manual work |

**Anticipated challenges**

- **Document quality:** University PDFs are often scanned images — OCR errors will reduce retrieval accuracy and need cleaning before embedding.
- **Ambiguous queries:** Students often ask vague questions ("what about the deadline?") without enough context — the system may retrieve irrelevant chunks.
- **Multi-document answers:** Some questions span multiple documents (e.g. both the exam rules and the student handbook), so the top-k retrieval may need to be tuned carefully to pull from the right source.
- **Keeping documents current:** If a regulation changes mid-year and the vector store is not updated, the chatbot will give outdated but confident-sounding answers.
