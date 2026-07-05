---
name: cache-consistency-after-gc
description: When testing document store garbage collection, the TG should verify
  that in-memory caches remain consistent with the underlying store. The bug is that
  VersionGarbageCollector can leave null/inconsistent entries in the document cache,
  causing NullPointerException when reading documents after GC.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# cache-consistency-after-gc

## Instructions

# Cache Consistency After Garbage Collection

## Instructions

- WHEN testing your document store's VersionGarbageCollector.gc() method or similar garbage collection logic
- THEN create a test that:
  1. Sets up a multi-cluster-node DocumentNodeStore environment (at least 2 cluster nodes with shared DocumentStore)
  2. Creates documents on one node and syncs them to the other node via `runBackgroundOperations()`
  3. Invokes `versionGarbageCollector.gc(1, TimeUnit.HOURS)` or similar GC method
  4. After GC completes, attempts to read back the documents using `store.getDocument("/test-<id>")` or similar accessor
  5. Asserts that the returned document is NOT null and contains the expected data (e.g., `assertNotNull("Document /test-X not found after GC", doc)`)

- The test must verify that after garbage collection, every document that existed before GC is still readable and non-null.
- A common pitfall is only testing that GC runs without exceptions — but GC can corrupt the cache while appearing to succeed. Always verify post-GC state by reading documents.
- Another pitfall is testing GC with only a single cluster node. The bug manifests specifically when documents created by one cluster node are cached on another node, and GC fails to properly refresh/evict stale cache entries.
- Example (correct):
```java
// Set up 2-node cluster
DocumentStore store = ...;
DocumentNodeStore ns1 = ...; // clusterId=1
DocumentNodeStore ns2 = ...; // clusterId=2
String id = "/test-" + System.nanoTime();
ns1.getDocument(id).set("prop", "val");
ns1.runBackgroundOperations();
ns2.runBackgroundOperations();
// GC on ns2
ns2.getVersionGarbageCollector().gc(1, TimeUnit.HOURS);
// VERIFY: document still readable and non-null
DocumentNodeStoreDelegate delegate = ...;
Document doc = delegate.getDocument(id);
assertNotNull("Document " + id + " not found after GC", doc);
assertEquals("val", doc.get("prop"));
```

- Example (incorrect — pitfall):
```java
// Only tests that GC doesn't throw
ns.getVersionGarbageCollector().gc(1, TimeUnit.HOURS);
// Missing post-GC read verification!
```

- When the bug is present, the post-GC read will throw a NullPointerException with a message like "Document /test-X not found" because the in-memory document cache contains a null entry for that document ID after GC.