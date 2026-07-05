---
name: document-recovery-test-setup-state
description: When testing recovery logic that depends on document state setup (like
  _modified timestamps and lastRev fields), the test must verify both the setup and
  the assertion logic match. This skill teaches how to validate recovery candidates
  that depend on correct document store state.
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# document-recovery-test-setup-state

## Instructions

# Document Recovery Test Setup State Validation

## Instructions

- WHEN the TG encounters a test for recovery functionality that relies on document store state, specifically methods like `getCandidates(long startTime)` which queries documents with `_modified >= startTime` and `_lastRev` values containing cluster node entries
- THEN the TG must verify that the test setup correctly populates the document store with the exact state the recovery logic expects. Specifically:
  - WHEN creating test documents that should be recovered (i.e., should appear as candidates), ensure each document has a `_modified` timestamp set to a value >= the `startTime` parameter passed to `getCandidates()`. Use `NodeDocument.getModifiedInSecs(timestamp)` to set the `_modified` field.
  - WHEN creating documents that should NOT be recovered, ensure their `_modified` timestamp is BEFORE the `startTime` parameter, or they have no matching `_lastRev` entry for the cluster node under test.
  - WHEN testing that recovery recovers no documents (expecting 0 recovered), all candidate documents returned by `getCandidates()` must have `_lastRev` entries that are already up-to-date for the cluster node, OR their `_modified` timestamps must be before `startTime` so they are excluded from the candidate list.
- Common pitfalls to avoid:
  - Setting `_modified` but using a timestamp that is too old (before `startTime`), causing the document to be excluded from candidates and the test to pass incorrectly
  - Not setting `_lastRev` values in the document store, causing `recoverCandidates()` to fail with NullPointerException or return incorrect counts
  - Assuming documents that exist in the store will automatically be recovery candidates — they must have both fresh `_modified` timestamps AND stale `_lastRev` entries
  - For root document, forgetting that `getCandidates(0)` returns it only if its `_modified` >= startTime (e.g., 0) and it has a stale lastRev for the cluster node

- Correct approach example:
```java
// Setup: create a document that SHOULD be a recovery candidate
String id = Utils.getIdFromPath("/testNode");
NodeDocument doc = new NodeDocument(store, id, null);
long now = System.currentTimeMillis();
doc.put("_modified", NodeDocument.getModifiedInSecs(now));
// Add a stale lastRev entry (old revision before the current root revision)
Revision oldRev = new Revision(now - 10000, 0, clusterId);
Revision currentRev = new Revision(now, 0, clusterId);
doc.put("_lastRev", Collections.singletonMap(String.valueOf(clusterId), oldRev));
store.create(Collection.NODES, Collections.singletonList(doc));

// Call the recovery with startTime < now
int recovered = agent.recoverCandidates(nodeInfo, now - 5000, now + 10000, "test");
assertEquals(1, recovered); // This document should be recovered
```

- Incorrect approach example:
```java
// WRONG: Document created but _modified is too old
doc.put("_modified", NodeDocument.getModifiedInSecs(now - 100000));
// _lastRev is stale but _modified is before startTime
int recovered = agent.recoverCandidates(nodeInfo, now - 5000, now + 10000, "test");
// Test passes because document is NOT a candidate (wrong reason)
assertEquals(0, recovered);
```