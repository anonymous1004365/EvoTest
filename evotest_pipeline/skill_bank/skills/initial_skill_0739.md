---
name: lucene-index-read-write-lock-handling
description: When testing Lucene index operations under concurrent read/write node
  locking, verify that write locks are acquired before indexing and released after
  completion, and that read locks are not leaked across indexing sessions. Use interleaved
  add/delete operations to trigger inconsistent lock states.
code_tags:
- CONCURRENCY
test_pattern: STATE_TEST
---

# lucene-index-read-write-lock-handling

## Instructions

# Lucene Index Read/Write Lock Handling

## Instructions

- WHEN the TG encounters a Lucene index implementation that uses `ReadWriteLock` (or similar read/write locking mechanism) to protect concurrent access to an index writer or searcher manager
- THEN it should test the scenario where document addition and deletion operations overlap, verifying that the lock is **not held by a different thread** after the operation completes
- Include concrete test steps:
  1. Insert documents into the index (e.g., via `jcr:title` or `jcr:description` properties)
  2. Delete some of those documents concurrently or in rapid succession
  3. Re-insert documents with the same path after deletion
  4. Verify no `IllegalMonitorStateException` (e.g., "attempt to unlock read lock, not locked by current thread") occurs during any indexing operation
- The test should catch the case where a read lock acquired during indexing is incorrectly released (unlocked) by a different lifecycle method or thread context than the one that acquired it
- Common pitfalls:
  - Testing only sequential add-then-query without interleaved add/delete cycles
  - Testing only single-threaded access without concurrent modification
  - Testing only the happy path where no rebalancing/reopening of the index occurs mid-operation
  - Assuming that acquiring a read lock and releasing it in the same method call is safe — the bug is that the release may happen in a different context than the acquisition

### Correct test pattern (conceptual):
```java
// Setup index with some docs
index("node1", "title", "hello");
index("node2", "title", "world");

// Delete and re-add in overlapping fashion
delete("node1", "title", "hello");
index("node1", "title", "hello-updated");

// Trigger index merge/refresh
session.save();

// Query — should not throw lock-related exceptions
assertNotNull(index.query("hello-updated"));
```

### Incorrect test pattern (would miss this bug):
```java
index("node1", "title", "hello");
session.save();
assertNotNull(index.query("hello"));
// Only sequential add-then-query — no overlapping add/delete to trigger lock re-entrance issue
```