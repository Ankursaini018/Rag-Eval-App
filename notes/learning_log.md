# Learning Log

## Day 7 — Baseline Pipeline Review

### 1. Cosine Similarity and Vector Normalization

I learned that cosine similarity measures how similar two vectors are based on the angle between them rather than their raw magnitude. This is useful for semantic search because documents and queries can have different vector magnitudes while still pointing in similar semantic directions. Normalizing vectors makes the comparison more consistent because the similarity becomes focused on direction instead of vector length. In the RAG pipeline, this affects how accurately the embedding search retrieves relevant document chunks.

### 2. BGE Query Prefix

I learned that the `BAAI/bge-small-en-v1.5` embedding model expects a specific instruction prefix on search queries:

`Represent this sentence for searching relevant passages: `

The prefix is applied to search queries but not to documents. This distinction matters because the model was trained to represent queries and passages differently. Applying the query instruction consistently helps the embedding space represent the user's question appropriately for retrieval.

### 3. Page-Level Chunking

I learned why the RAG pipeline keeps chunks within page boundaries instead of allowing chunks to cross from one page into another. The evaluation dataset uses page-level source labels, so each retrieved chunk needs to remain associated with the page from which it originated. If a chunk crosses page boundaries, the source label can become ambiguous and make retrieval evaluation less reliable. Keeping chunks page-local makes it possible to compare retrieved pages against the expected source pages.

### 4. Windows curl Alias and API Model Issues

I learned that the `curl` command behaves differently in Windows PowerShell because `curl` can resolve to PowerShell's `Invoke-WebRequest` alias instead of the actual curl executable. Using `curl.exe` avoids that ambiguity and allows the normal curl command-line behavior.

I also encountered an API model issue where a Groq model could return a model-not-found error. This showed me that an application can fail even when the API key and request structure are correct if the requested model is no longer available. Model configuration therefore needs to be treated as part of the application's configuration rather than assuming that a model name will remain available forever.

### 5. What the Day 6 Answer Set Taught Me

The Day 6 answer set showed me that evaluating a RAG system requires more than checking whether an answer sounds correct. Each answer needs to be checked against both the retrieved chunks and the cited source passage.

The most useful distinction is between retrieval failure, ranking failure, generation failure, and problems with the question or source document. A retrieval miss means the correct information was not retrieved at all. A ranking problem means the correct chunk was retrieved but ranked too low. A generation problem means the correct context was available but the generated answer still failed to use it correctly. A bad question or bad document can make the evaluation unreliable before retrieval or generation is even considered.

The Day 6 score and the most common failure cause will be used as baseline evidence for the improvements made later in the project.

## LLM Setup

The project uses:

- Provider: Groq
- Model: `openai/gpt-oss-20b`
- Reasoning effort: `low`
- Environment variable: `LLM_REASONING_EFFORT=low`

The same LLM should be used throughout the project so that before-and-after evaluation results remain comparable. Changing the model during the project would make it difficult to determine whether an improvement came from the RAG pipeline changes or from a different language model.

## Day 11 — Baseline retrieval evaluation

The baseline retrieval scores are recall@1 = 0.591, recall@3 = 0.807, recall@5 = 0.864, and MRR = 0.774. The gap between recall@1 and recall@5 shows that the correct page is often retrieved, but it is not always ranked first. The strongest question type was tricky, while multi_chunk was the weakest on recall@5. Looking at the CSV, some of the missed questions appear to be cases where the relevant page was not retrieved in the top five, while others are cases where retrieval found the right page but ranked it lower. This suggests that both finding the correct page and ranking retrieved pages are relevant weaknesses, with recall@5 indicating the larger retrieval-coverage issue. One surprising result is that tricky questions performed better than expected compared with multi_chunk and paraphrase questions. These numbers are the baseline, so they should be treated as the starting point for later analysis rather than as a reason to change the golden set or retrieval configuration.