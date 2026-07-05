---
name: modified-timestamp-monotonic-update
description: When testing document metadata updates based on revisions, verify that
  a newer modified timestamp is never reset by a later operation carrying an older
  revision timestamp. This skill catches bugs where update operations use plain set
  semantics instead of max/monotonic semantics for _modified-like fields.
code_tags:
- MODIFIED_TIMESTAMP_RESET
- REVISION_OVERWRITE
- STATE_CONSISTENCY
test_pattern: STATE_TEST
---

# modified-timestamp-monotonic-update

## Instructions

## Instructions

- WHEN the TG encounters code that stores a document modified timestamp, last-modified field, revision time, checkpoint time, or similar monotonic metadata derived from revisions,
- THEN it should test that applying an older revision after a newer one does not decrease the stored value.
- Create or update a document with a newer revision timestamp first, then apply an update using an older revision timestamp.
- Assert that the stored modified timestamp remains equal to the newer timestamp, not the older timestamp.
- If the code exposes an UpdateOp-like abstraction, inspect or apply the operation and verify it uses max/monotonic behavior rather than unconditional set behavior.
- Include a follow-up query or wait condition when available, because timestamp regression often appears as stale polling, missed visibility, or a failed time comparison.

## Common Pitfalls

- Do not test only increasing timestamp order; the bug requires an out-of-order older revision after a newer one.
- Do not assert merely that the field exists. Assert the exact monotonic value after both updates.
- Do not rely on wall-clock sleeping when deterministic revision timestamps can be constructed.