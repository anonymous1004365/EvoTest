---
name: newest-revision-null-check-inter-cluster
description: When testing methods that look up the newest revision of a document across
  multiple cluster nodes, the test must verify the method does not return null when
  a valid revision exists. This skill applies to tests involving getNewestRevision()
  or similar revision-lookup methods in a multi-cluster-node DocumentNodeStore setup.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# newest-revision-null-check-inter-cluster

## Instructions

# Newest Revision Null Check Across Cluster Nodes

## Instructions

- **WHEN** the TG is testing `DocumentNodeStore.getNewestRevision()` or a similar method that retrieves the newest revision of a document for a given cluster node's head revision, on a `NodeDocument` that was created by a **different cluster node** (e.g., `ns1` creates the document, `ns2` looks up its newest revision)
- **THEN** the TG must call `doc.getNewestRevision(ns2, ns2.getHeadRevision())` and assert that the result is **not null**, using `assertNotNull()`. The test should verify that the returned `Revision` object's cluster ID matches the expected cluster node (e.g., `assertEquals(1, newest.getClusterId())`).
- **INCLUDE** a setup that creates a document under one cluster node (e.g., `ns1`), then uses `ns1.newRevision()` to create a change revision and commits it via `commit()` before querying the document. The test **must** include both `ns1` (the creating node) and `ns2` (the querying node) as separate `DocumentNodeStore` instances sharing the same underlying `DocumentStore`, and both must have `setAsyncDelay(0)`.
- **AVOID** the common pitfall of only testing `getNewestRevision()` with the same cluster node that created the document — the bug only manifests when a **different** cluster node queries the revision. Avoid also the pitfall of forgetting to call `runBackgroundOperations()` or `commit()` on the creating node, which is necessary for the revision to be visible to other nodes.

### Incorrect Test (missing cross-node null check)
```java
// Buggy: only tests getNewestRevision from the creating node (ns1)
Revision newest = doc.getNewestRevision(ns1, ns1.getHeadRevision());
assertNotNull(newest);
// Missing: test from ns2's perspective — this would not catch the null bug
```

### Correct Test (includes cross-node null check)
```java
// Correct: tests getNewestRevision from both creating and querying nodes
DocumentNodeStore ns1 = builderProvider.newBuilder().setAsyncDelay(0)
        .setDocumentStore(store).setClusterId(1).getNodeStore();
DocumentNodeStore ns2 = builderProvider.newBuilder().setAsyncDelay(0)
        .setDocumentStore(store).setClusterId(2).getNodeStore();

// ns1 creates and commits a document
String id = Utils.getIdFromPath("/test");
Revision rev = ns1.newRevision();
Document doc = new Document(store);
NodeDocument.setRevision(doc, rev, "c");
doc.put(Document.MODIFIED_IN_SECS, ...);
store.create(NODES, singletonList(doc));

// ns2 queries for the newest revision — must NOT return null
Revision newest = doc.getNewestRevision(ns2, ns2.getHeadRevision());
assertNotNull("getNewestRevision returned null for cross-node query", newest);
assertEquals(1, newest.getClusterId());
```