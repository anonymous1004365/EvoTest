---
name: intermediate-doc-count-gc-verification
description: WHEN testing version garbage collection of intermediate documents with
  timestamps near collection boundaries, THEN verify the exact count of collected
  documents by comparing before-and-after state, not just checking for exceptions.
  The bug was that intermediate documents with timestamps exactly at the collection
  boundary were incorrectly counted.
code_tags:
- STATE_MUTATION
- COUNT_MISMATCH_FIXED_MILLISECONDS
test_pattern: STATE_TEST
---

# intermediate-doc-count-gc-verification

## Instructions

# Intermediate Document Garbage Collection Count Verification

## Instructions

- WHEN the TG encounters a VersionGarbageCollector (or similar) that collects intermediate documents (sprint/intermediate nodes) based on timestamps
- THEN it should create a test that:
  1. Sets up a known number of intermediate documents with timestamps exactly at the collection boundary (e.g., using `setModified` to exactly `COLLECT_INTERMEDIATE_OPS_CREATION_TS` or similar boundary field)
  2. Records the count of documents before garbage collection
  3. Runs garbage collection with the relevant parameters (e.g., `collectIntermediateDocs` or `gcIntermediateDocs`)
  4. Records the count of documents after garbage collection
  5. Asserts that the difference (collected count) matches the expected number of documents that should have been collected
  6. Asserts that the remaining documents count matches expectations (documents NOT at the boundary should survive)

- WHEN setting up test data for intermediate document GC
- THEN use exact timestamp values that exercise the boundary condition — include documents with timestamps BEFORE, AT, and AFTER the collection boundary
- THEN use `createIntermediateDoc` or equivalent helper methods to create intermediate documents with specific timestamps

- WHEN asserting the GC result
- THEN assert on the exact count of removed documents (before minus after), NOT just that no exception was thrown
- THEN use an assertion like `assertEquals(expectedRemoved, beforeCount - afterCount)` with a descriptive failure message

- Common pitfalls to avoid:
  - **Testing only with documents far from the boundary**: Documents with timestamps far before/after the boundary may always work; the bug manifests specifically at the boundary timestamp value itself
  - **Asserting only that GC completes without error**: The bug is an off-by-one/incorrect boundary check — the GC may run without exceptions but collect fewer or more documents than expected
  - **Using a single document**: Create multiple documents (at least 10) to verify counting logic, as the bug manifests in the count
  - **Not controlling document timestamps precisely**: Use `AbstractDocumentStore.set()` or `NodeStore.setModified()` with exact millisecond precision timestamps

- Example of a correct test pattern:
  ```java
  // Create documents with timestamps at and around the boundary
  int before = countIntermediateDocs();
  // ... create 3 docs at boundary (should be collected)
  // ... create 2 docs after boundary (should survive)
  gc();
  int after = countIntermediateDocs();
  // Verify exactly 3 docs were collected
  assertEquals("Expected 3 intermediate docs collected", 3, before - after);
  ```

- Example of an INCORRECT test (missing count verification):
  ```java
  // WRONG: only checks no exception
  gc();
  // No assertion on how many documents were collected!
  ```