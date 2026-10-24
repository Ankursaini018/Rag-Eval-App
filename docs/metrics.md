# Retrieval metrics in plain language

All metrics compare the **pages** of the retrieved chunks with the **gold pages** of each golden question.
Page-level labels mean the scores stay comparable when the chunk size changes.
Unanswerable questions (no gold page) are not scored here; the answer evaluation covers them.

## Recall@k
*Of the pages that hold the answer, how many are in the top k results?*

- One gold page: the score is 1 if it is in the top k, otherwise 0.
- Two gold pages (multi-chunk question): finding one gives 0.5, both gives 1.
- The reported number is the average over all questions.
- I report k = 1, 3 and 5. The app gives the LLM 5 chunks, so **recall@5 is the ceiling**:
  if the right page is not in those 5 chunks, the LLM cannot answer from it.

## MRR (Mean Reciprocal Rank)
*How near the top does the first correct page appear?*

- Score per question = 1 / rank of the first gold page. Rank 1 = 1.0, rank 2 = 0.5, rank 3 = 0.33, not found = 0.
- MRR is the average over all questions. It is measured over the top 10 results.
- Recall@5 cannot tell rank 1 from rank 5. MRR can. Rerankers should raise MRR.

## Worked example
Three questions, each with one gold page:

| Question | Rank of the gold page | recall@1 | recall@3 | reciprocal rank |
|---|---|---|---|---|
| A | 1 | 1 | 1 | 1.00 |
| B | 2 | 0 | 1 | 0.50 |
| C | not in the top 10 | 0 | 0 | 0.00 |
| **average** | | **0.33** | **0.67** | **0.50 (= MRR)** |

## Reading the numbers
- High recall@5 but low MRR: the right page is found but ranked low. Try a reranker.
- Low recall@5: the page is not found at all. Try other chunking, BM25 or hybrid search, or query rewriting.
- With 50 questions (about 44 scored), one question is worth about 2 percentage points. Differences
  of 1-2 questions are noise, not proof.
- These metrics say nothing about whether the final answer is correct. That is the faithfulness
  and answer evaluation.