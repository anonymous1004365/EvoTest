---
name: rollback-deletedonce-flag-restoration
description: When testing document store rollback logic that involves conflicting
  node creation/deletion, verify that the _deletedOnce flag is properly restored on
  documents after a commit retry / rollback cycle. The TG should check that a node
  created by a conflicting commit and then rolled back still has _deletedOnce set,
  ensuring the flag survives the rollback.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- EDGE_CASE_INPUT
- CONCURRENCY
- STATE_MUTATION
- DOCUMENT_ROLLBACK_RECOVERY
test_pattern: STATE_TEST
---

# rollback-deletedonce-flag-restoration

## Instructions

# Rollback _deletedOnce Flag Restoration

## Instructions

- WHEN the TG encounters code that performs a **commit, rollback, or retry** in the context of a `DocumentNodeStore` or similar document-based store, and the store tracks a `_deletedOnce` flag on documents (indicating a node was at some point deleted):
  - THEN the TG should write a test that:
    1. Obtains the `DocumentNodeStore` and the underlying `DocumentStore` (e.g., `MemoryDocumentStore`).
    2. Gets the root node builder, creates a child node (e.g., `child("newConflictingNode")`), sets a property (e.g., `"prop"`), and merges.
    3. Simulates a **conflicting commit** that deletes that node — for example, by using a second `DocumentNodeStore` with a different cluster ID, merging a delete of the same node.
    4. On the original store, creates another child with the **same name** (e.g., `child("newConflictingNode")`), sets a property, and attempts to merge. This will fail with a `CommitFailedException` due to a conflict.
    5. **Retries the merge**: calls `store.merge(builder, ...)` again (after re-acquiring the builder from the root).
    6. After the retry succeeds, directly reads the underlying document from the `DocumentStore` (e.g., `store.getDocumentStore().find(NODES, Utils.getIdFromPath("/newConflictingNode"))`).
    7. Asserts that the document contains a `_deletedOnce` property (or equivalent flag) — i.e., `assertTrue("document should get _deletedOnce marked due to rollback", doc.has("_deletedOnce"))`.
  - The test should verify that even after a rollback of a conflicting delete, the node's `_deletedOnce` flag is **preserved**, not lost.
  - Avoid **common pitfalls**:
    - **Do not** only test the success path where there is no conflict — the bug only manifests when a conflict triggers a rollback/retry.
    - **Do not** forget to retry the merge after the conflict: the rollback and retry is what causes the flag to be lost.
    - **Do not** check only via the `NodeStore` API (`getRoot().hasChildNode(...)`) — the flag `_deletedOnce` is a low-level document property that must be verified directly on the `DocumentStore` level.
    - **Do not** assume that the merge retry will silently restore all flags — the bug shows that `_deletedOnce` is lost unless explicitly handled.

- WHEN the TG writes such a test:
  - THEN the test should expect that on the **buggy** version, the assertion `doc.has("_deletedOnce")` fails (the flag is missing).
  - On the **fixed** version, the same test passes (the flag is present).

- **Correct example** (pseudocode):
  ```java
  DocumentNodeStore store = builderProvider.newBuilder().getNodeStore();
  DocumentStore ds = store.getDocumentStore();
  
  // Create node via store1
  NodeBuilder b1 = store.getRoot().builder();
  b1.child("newConflictingNode").setProperty("prop", "val");
  store.merge(b1, EmptyHook.INSTANCE, CommitInfo.EMPTY);
  
  // Conflicting delete via store2
  DocumentNodeStore store2 = builderProvider.newBuilder().setClusterId(2).getNodeStore();
  NodeBuilder b2 = store2.getRoot().builder();
  b2.child("newConflictingNode").remove();
  store2.merge(b2, EmptyHook.INSTANCE, CommitInfo.EMPTY);
  store2.runBackgroundOperations();
  store.runBackgroundOperations();
  
  // Try to create same node again on store1 — will conflict
  NodeBuilder b3 = store.getRoot().builder();
  b3.child("newConflictingNode").setProperty("prop", "val");
  try {
      store.merge(b3, EmptyHook.INSTANCE, CommitInfo.EMPTY);
      fail("should have thrown");
  } catch (CommitFailedException e) { /* expected */ }
  
  // Retry merge
  NodeBuilder b4 = store.getRoot().builder();
  b4.child("newConflictingNode").setProperty("prop", "val2");
  store.merge(b4, EmptyHook.INSTANCE, CommitInfo.EMPTY);
  
  // Verify _deletedOnce is still set on the underlying document
  String id = Utils.getIdFromPath("/newConflictingNode");
  NodeDocument doc = ds.find(NODES, id);
  assertTrue("document should get _deletedOnce marked due to rollback", doc.has("_deletedOnce"));
  ```

- **Incorrect example** (would miss the bug):
  ```java
  // Only testing creation, no conflict → never hits bug
  NodeBuilder b = store.getRoot().builder();
  b.child("node").setProperty("p", "v");
  store.merge(b, EmptyHook.INSTANCE, CommitInfo.EMPTY);
  // Does NOT trigger rollback of a conflicting delete → _deletedOnce never involved
  ```