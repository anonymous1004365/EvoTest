---
name: document-split-commit-root-path
description: When tests involve document splitting with commit roots, the test must
  verify that getCommitRootPath resolves paths correctly for split document entries
  referencing the previous document. Without this check, splitting can produce invalid
  commit root paths.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# document-split-commit-root-path

## Instructions

# Document Split Commit Root Path Validation

## Instructions

- WHEN the TG encounters test code that triggers a `DocumentStore.splitDocuments()` operation — specifically a scenario where a commit root entry in a split document references a revision whose path is stored in the **previous** document — THEN the TG must test that `NodeDocument.getCommitRootPath(Revision)` resolves the correct absolute path.

- The TG should verify that after splitting, when a document entry's `_commitRoot` revision points to a path stored in the previous document segment, calling `getCommitRootPath(rev)` returns a path **prefixed with the previous document's path** (e.g., `/B/C`), not just a single slash `/`.

- To write the test: create a scenario where:
  1. Multiple revisions are committed to a node at path like `/B/C`
  2. `DocumentStore.splitDocuments()` is called (e.g., via a background split operation)
  3. After the split, the commit root entry for one revision ends up in a **previous** document segment
  4. Call `NodeDocument.getCommitRootPath(rev)` on that revision and verify the result

- The test MUST expect that on the **buggy** version, `getCommitRootPath(rev)` returns an incorrect path (e.g., just `"/"`) when the commit root is in the previous document, while on the **fixed** version it returns the full path (e.g., `"/B/C"`).

- **Common pitfalls to avoid:**
  - ❌ Testing only `getCommitRootPath` on revisions where the commit root is in the same document — this will not expose the bug.
  - ❌ Assuming that `getCommitRootPath` always works correctly — the bug only manifests when the commit root entry resides in a **previous** document segment after a split.
  - ❌ Forgetting to actually perform the document split before calling `getCommitRootPath` — the bug is only triggered when the document has been split.

- **Correct approach (example logic):**
  ```java
  // Perform operations that cause a document split
  // where commit root path is stored in the previous document
  NodeDocument doc = ...;
  Revision rev = ...;  // a revision whose commit root is in prev doc
  String path = doc.getCommitRootPath(rev);
  // Expected: path should contain the full path (e.g., "/B/C")
  assertTrue("Commit root path should include full path", path.contains("/B/C"));
  ```

- **Incorrect approach (missing the split scenario):**
  ```java
  // ❌ Only testing getCommitRootPath on non-split documents
  NodeDocument doc = ...;
  String path = doc.getCommitRootPath(someRevision);
  assertEquals("/", path);  // This passes for both buggy and fixed!
  ```