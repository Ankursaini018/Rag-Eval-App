# Golden set writing guidelines

The golden set (`data/golden.jsonl`) is the yardstick for every experiment in this project.
If it is wrong, every number built on it is wrong. These are the rules I follow.

## Format

- One JSON object per line. Fields: `id`, `question`, `type`, `answer`, `gold`, optional `notes`.
- `gold` lists `{doc, page}` pairs, at page level so labels survive chunk-size changes.
- Run `python scripts/validate_golden.py --pages` after every few additions.

## Writing a question

1. Write what a real user would ask, not "what does the text say about X".
2. The question must make sense without the document in front of the reader.
3. Write the reference answer in my own words, only with facts the cited pages contain.
4. Cite every page needed for the answer, and no page that is not needed.
5. Check the answer against the source page again, the next day if possible.

## Types

- **single_fact**: one fact stated in one place.
- **multi_chunk**: needs 2 or more different pages; neither page answers it alone.
- **unanswerable**: the documents do not contain the answer. `answer` is null, `gold` is [].
  Include near-misses (on topic, detail missing), not only off-topic questions.
  Prove absence with `scripts/show_page.py --find` using several phrasings.
- **paraphrase / tricky**: added later; wording differs from the documents or contains a trap.

## Avoid

- Copying a sentence from the document into the question (the match becomes trivial).
- Yes/no questions, which can be guessed without retrieval.
- Several questions that all hit the same page.
- Letting an LLM write the questions or answers: it would test the pipeline against itself.
- Tuning questions after seeing results. If a question is bad, fix it and note it in the commit.

## Coverage target

Questions spread across many documents; 10% or more unanswerable; at least 10% need 2+ pages.