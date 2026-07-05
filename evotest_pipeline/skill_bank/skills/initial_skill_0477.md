---
name: clustered-split-revision-count
description: WHEN the TG encounters operations that split revisions in a multi-cluster-node
  document store, THEN it should verify that revision counts are correct across all
  cluster nodes by testing with multiple explicitly configured cluster nodes and checking
  background split operations complete correctly. This skill catches bugs where cached
  or background split operations fail to account for changes from other cluster nodes.
code_tags:
- CLUSTERED_OPERATIONS
- CACHE_OPERATIONS
test_pattern: STATE_TEST
---

# clustered-split-revision-count

## Instructions

# Clustered Split Revision Count Validation

## Instructions

**WHEN** the TG encounters a test for document revision splitting in a clustered document store (e.g., `DocumentMK`, `DocumentNodeStore`, `SplitOperations`) where multiple cluster nodes are involved:

- **THEN** the TG MUST verify that background split or revision cleanup operations (`runBackgroundSplitOperations`, `runBackgroundOperations`, `splitRevisions`) correctly account for revisions created by ALL cluster nodes, not just the local node.
- **THEN** the TG MUST create tests that use explicit `DEFAULT_CLUSTER_ID` values for multiple cluster nodes (e.g., `clusterIds = new int[]{1, 2, 3, 4, 5, 6, 7, 8, 9}`) and create documents (e.g., via `addNodes`, `setProperty`, `commit`) from multiple different cluster node stores concurrently or sequentially.
- **THEN** the TG MUST verify that after splitting, the number of previous documents or revision entries equals the expected count (e.g., `assertEquals("expected 2 split doc but found " + ..., 2, ...)`) across ALL cluster nodes, not just the node that initiated the split.
- **THEN** the TG MUST NOT assume that a split operation performed on one cluster node will correctly account for revision state on other cluster nodes without explicitly verifying cross-cluster state.
- **Common Pitfalls:**
  - Testing split operations with only a single cluster node, which may mask bugs where revision updates from other nodes are ignored
  - Verifying revision count or split document count only on the node that performed the split, without checking other nodes
  - Not explicitly setting cluster IDs via `DEFAULT_CLUSTER_ID` and relying on default single-node behavior

**Example (correct):**

```java
// Create stores for multiple cluster nodes
int[] clusterIds = new int[]{1, 2, 3, 4, 5, 6, 7, 8, 9};
DocumentMK[] stores = new DocumentMK[clusterIds.length];
for (int i = 0; i < clusterIds.length; i++) {
    stores[i] = new DocumentMK.Builder()
            .setAsyncDelay(0)
            .setClusterId(clusterIds[i])
            .open();
}
// Create and commit content from multiple nodes
for (int i = 0; i < 10; i++) {
    for (DocumentMK store : stores) {
        store.commit("/", "+\"node" + i + "\" : {\"prop\": \"value\"}");
    }
}
// Run background split operations on each node
for (DocumentMK store : stores) {
    store.runBackgroundSplitOperations();
}
// Verify the expected document count after splitting
assertEquals("expected 2 split doc but found " + ..., 2, ...);
```

**Example (incorrect — buggy pattern):**

```java
// Using only a single cluster node
DocumentMK store = new DocumentMK.Builder().open();
// commits...
store.runBackgroundSplitOperations();
// Only checking the single node's state — misses cross-node bugs
```