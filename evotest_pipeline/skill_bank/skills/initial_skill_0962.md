---
name: fs-index-status-tracking-on-close
description: When a Lucene index writer is closed after writing to a file-system-backed
  directory, the closeWriter method must also update the index definition's status
  child node so that the IndexTracker can detect changes. Without this, re-opening
  the index after close fails to find the index data.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# fs-index-status-tracking-on-close

## Instructions

# File-System Index Status Tracking on Writer Close

## Instructions

- WHEN the TG encounters code that uses `LuceneIndexEditorContext.closeWriter()` after writing index data to a file-system-backed (FSDirectory) Lucene index
- THEN the TG should verify that `closeWriter()` not only closes the `IndexWriter` but **also persists status metadata** (like `lastUpdated` and `indexedNodes`) to the index definition's `":status"` child node. Specifically, the test should:
  1. Create a `NodeBuilder` with a `PERSISTENCE_PATH` property pointing to a temporary file-system directory
  2. Obtain an `IndexWriter` via `getWriter()` (which opens an `FSDirectory`)
  3. Perform at least one index update (so `indexedNodes > 0`)
  4. Call `closeWriter()`
  5. Verify that `definition.getChildNode(":status").exists()` is `true`
  6. Verify that `":status"` contains a `"lastUpdated"` property (of type `Type.DATE`) and an `"indexedNodes"` property

- **Common pitfalls to avoid:**
  - Testing only the in-content (OakDirectory) path without testing the file-system (FSDirectory) path
  - Checking that `closeWriter()` closes the writer but forgetting to check that status metadata was written to the `NodeBuilder`
  - Using `definition` directly instead of `definition.getChildNode(":status")` to check status properties
  - Assuming that simply closing the `IndexWriter` is sufficient for the `IndexTracker` to detect changes — the status node is essential for that detection when using `FSDirectory`

- **Correct example (Java):**
  ```java
  NodeBuilder defBuilder = ...; // create index definition
  defBuilder.setProperty(PERSISTENCE_PATH, tempDir.getAbsolutePath());
  defBuilder.setProperty(PERSISTENCE_NAME, PERSISTENCE_FILE);
  LuceneIndexEditorContext ctx = new LuceneIndexEditorContext(defBuilder, analyzer, callback);
  IndexWriter writer = ctx.getWriter();
  // ... perform some indexing ...
  ctx.incIndexedNodes(); // simulate indexing one node
  ctx.closeWriter();
  
  NodeBuilder status = defBuilder.getChildNode(":status");
  assertTrue("Status node should exist after closeWriter", status.exists());
  assertNotNull("lastUpdated should be set", status.getProperty("lastUpdated"));
  assertNotNull("indexedNodes should be set", status.getProperty("indexedNodes"));
  ```

- **Incorrect example (would miss the bug):**
  ```java
  // Only testing with OakDirectory (no PERSISTENCE_PATH set)
  NodeBuilder defBuilder = ...;
  LuceneIndexEditorContext ctx = new LuceneIndexEditorContext(defBuilder, analyzer, callback);
  ctx.getWriter();
  ctx.closeWriter(); // only checks no exception thrown, but doesn't verify status node
  ```