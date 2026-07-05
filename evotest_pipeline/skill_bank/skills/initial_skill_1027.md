---
name: revision-cache-read-boundary
description: When testing revision lookup logic that scans local and previous document
  changes, verify not only the returned newest revision but also that the lookup stops
  after the first relevant change. This skill catches bugs where correct answers are
  produced through excessive reads of previous documents or split documents.
code_tags:
- REVISION_CACHE_READS
- PERFORMANCE_LOOP_COST
- TRIGGER_EXCESSIVE_RPC_CALLS
test_pattern: PERFORMANCE_TEST
---

# revision-cache-read-boundary

## Instructions

## Instructions

- WHEN the TG encounters code that computes the newest visible revision by merging local revisions, commit roots, previous documents, split documents, or lazily fetched revision history,
- THEN it should write a test that verifies both semantic correctness and bounded read behavior.
- Build a fixture with one relevant newest revision and several older previous/split documents that would be expensive to scan.
- Wrap or mock the document store/read source so the test can count calls or iterator consumption.
- Call the revision lookup method and assert the expected newest revision is returned.
- Also assert that the implementation reads only the minimal previous document range, for example one read instead of scanning every old document.
- Prefer tests that expose lazy iteration and early-abort behavior, such as an iterator that fails if it is consumed beyond the necessary element.

## Common Pitfalls

- Do not test only the returned revision; the buggy implementation may return the correct revision while performing too many backend reads.
- Do not use a fixture with only one previous document, because it cannot reveal an accidental full scan.
- Do not hide the cost behind an in-memory collection without counting document-store reads or iterator advancement.