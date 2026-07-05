---
name: concurrent-gc-during-active-sessions
description: When a garbage collection operation modifies or deletes documents while
  concurrent sessions are actively querying the same paths, the test must exercise
  this interleaving to catch DocumentStoreException race conditions.
code_tags:
- CONCURRENCY
test_pattern: INTERACTION_TEST
---

# concurrent-gc-during-active-sessions

## Instructions

# Concurrent GC During Active Sessions

## Instructions

- WHEN the TG encounters a VersionGarbageCollector or similar GC component that asynchronously deletes or modifies documents, AND there are concurrent client sessions that may be querying the same document paths (e.g., via `getChildren`), THEN the test must simulate the interleaving:
  1. Start a GC operation (e.g., `VersionGarbageCollector.gc()`) on a background thread.
  2. While the GC is in progress, have a foreground session repeatedly query for children of a path that the GC is actively targeting (e.g., `/node`).
  3. Verify that no `DocumentStoreException` is thrown from the query operations during the GC.
  4. Wait for GC to complete and confirm no exceptions were thrown.

- When the GC's `collectReferences` or document deletion methods execute concurrently with `NodeStore.getChildren` or similar traversal methods, the test must check for `DocumentStoreException` containing "Error occurred while fetching children" — this is the key symptom of a race condition where the GC deletes intermediate nodes while another session navigates them.

- Common pitfall: Running GC synchronously or to completion before testing client operations, which masks the race condition. The interleaving must be racy — GC must run concurrently with queries.

- Example of CORRECT test pattern:
```java
// GC thread
ExecutorService executor = Executors.newSingleThreadExecutor();
Future<Void> gcFuture = executor.submit(() -> {
    versionGarbageCollector.gc();
    return null;
});

// Concurrent query loop while GC is running
for (int i = 0; i < 100; i++) {
    try {
        root.getTree("/node").getChildren();  // or similar traversal
    } catch (DocumentStoreException e) {
        fail("Concurrent GC caused DocumentStoreException: " + e.getMessage());
    }
    Thread.sleep(10);
}
gcFuture.get(30, TimeUnit.SECONDS);
```

- Example of INCORRECT test pattern (misses the bug):
```java
// GC runs to completion first — no interleaving
versionGarbageCollector.gc();

// Then queries — GC is already done, no race
root.getTree("/node").getChildren();
```

- The test should also verify that the GC operation itself succeeds (no exception from the GC future) to confirm the race does not corrupt the GC process either.