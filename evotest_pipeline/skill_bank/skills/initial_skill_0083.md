---
name: file-sortby-respecting-file-order
description: WHEN the TG encounters file consumer endpoints using sortBy with file:path
  ordering, THEN it should test that files in different subdirectories are correctly
  ordered by their relative path (not just file name). This skill prevents bugs where
  sortBy sorts files from different directories incorrectly due to incomplete path-based
  comparisons.
code_tags:
- SAFE_COPY
- IDEMPOTENT_CONSUMER
- FILE_IDEMPOTENT_REPOSITORY
test_pattern: STATE_TEST
---

# file-sortby-respecting-file-order

## Instructions

# File sortBy Must Correctly Order Files Across Subdirectories

## Instructions

**WHEN** the TG encounters a file consumer endpoint that uses the `sortBy` option (e.g., `sortBy=file:path`) to order consumed files, especially with `recursive=true` and files placed in multiple subdirectories:

- **THEN** the TG should create a test that places files in multiple subdirectory levels (e.g., root, sub/, sub/sub2/) with names that would sort differently than their full paths
- **THEN** the TG should verify that the files are consumed in the order expected by `file:path` sorting (alphabetical by full relative path), not by file name alone
- **THEN** the TG should use `MockEndpoint.assertMockEndpointsSatisfied()` with `expectedBodiesReceived()` to assert the exact order of consumed messages
- **THEN** the TG should verify the `GenericFile` property (`Exchange.FILE_EXCHANGE_FILE`) to validate the actual file path of each consumed message

**Concrete example:**
The bug occurred when three files were placed in:
- `target/multidir/bye.txt` (path: `bye.txt`)
- `target/multidir/sub/hello.txt` (path: `sub/hello.txt`)
- `target/multidir/sub/sub2/godday.txt` (path: `sub/sub2/godday.txt`)

With `sortBy=file:path`, the expected order (by relative path string) is:
1. `bye.txt`
2. `sub/hello.txt`
3. `sub/sub2/godday.txt`

But the buggy version sorted by file name only, producing `bye.txt`, `godday.txt`, `hello.txt`.

**Mistakes to avoid:**
- Do NOT test sortBy with files all in the same directory — that won't catch cross-directory ordering bugs
- Do NOT rely only on body content to verify ordering without checking actual file paths
- Do NOT forget to set `delete=true` and `initialDelay=0&delay=10` to ensure clean, timely consumption in tests
- Do NOT assume `file:path` orders by the file name portion — it should order by the **full relative path** including subdirectory prefixes