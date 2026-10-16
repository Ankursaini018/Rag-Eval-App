# Learning log
One entry per day: what I built, what surprised me, what I'd explain in an interview.

## Day 1: <date>
- Topic chosen:
- Why this topic (can I tell a right answer from a wrong one?):
- Documents collected:
- Something I learned:
- Question I still have:

## Day 2: embeddings and similarity
- An embedding is: <your own words, 1 sentence>
- Cosine similarity measures: <your own words>
- Queries get a prefix and documents don't because: <your own words>
- Experiment results: <what worked, what failed, with 1-2 example queries and their top scores>
- A surprise: 
- Question for later:

## Day 3: parsing
- Why page numbers matter: <your words>
- Pages parsed: <N pages from M documents>. Pages flagged by check_pages.py: <N>
- Problems found (real examples from MY documents):
  1. <e.g. "doc X page 4 had hyphen-split words"> -> fixed by <...>
  2. <e.g. "doc Y is a scan with no text"> -> removed / needs OCR
- Surprise: 
- Why headers/footers hurt search: <your words>

## Day 4: chunking
- A token is: <your words>. Why not count words: <...>
- Overlap exists because: <your words>
- My numbers (size 500, overlap 50): <N chunks, avg tokens, tiny chunks>
- A chunk I read that looks bad (cut mid-sentence? mostly code?): <doc, page, what's wrong>
- A guess for Day 15: will smaller or larger chunks retrieve better, and why?
