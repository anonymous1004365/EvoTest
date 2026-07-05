---
name: cluster-node-restart-dispose-reuse
description: Tests that dispose and reuse a DocumentNodeStore should simulate real
  cluster node restarts. When a DocumentNodeStore is disposed and then re-initialized
  with the same cluster node info, the test must verify the store can be successfully
  used after the restart cycle without stale state or initialization failures.
code_tags:
- RESOURCE_MANAGEMENT
- STATE_MUTATION
- CLUSTER_ID_INITIALIZATION
test_pattern: STATE_TEST
---

# cluster-node-restart-dispose-reuse

## Instructions

# Cluster Node Restart: Disposing and Reusing DocumentNodeStore

## Instructions

This skill applies when testing lifecycle management of `DocumentNodeStore` instances, particularly scenarios that simulate a cluster node restart.

- WHEN testing `DocumentNodeStore` disposal and re-initialization (i.e., calling `dispose()` on one instance and then creating a new `DocumentNodeStore` with the same `DocumentMK.Builder` or cluster node configuration),
- THEN the test MUST:
  1. Call `dispose()` on the first `DocumentNodeStore` instance.
  2. Obtain a **new** `DocumentNodeStore` instance (e.g., via `builder.getNodeStore()` or creating a new builder with the same `DocumentStore` backend).
  3. Verify that the new instance is usable: call methods like `getNodeState()`, `getRoot()`, or perform a `getNode("/")` traversal and assert that it returns a non-null, valid state.
  4. Assert that the new instance does NOT throw exceptions related to stale cluster state, disposed background threads, or invalid cluster node info.
  5. Dispose the new instance after verification to avoid resource leaks.

- Common pitfalls to avoid:
  - **Assuming `dispose()` is idempotent or can be called multiple times**: Test the path where dispose is called exactly once, then a new instance is created. Do NOT test calling dispose() twice on the same instance.
  - **Not verifying the new instance's functionality**: Merely creating a new `DocumentNodeStore` after disposal without calling any methods on it may not trigger the bug. Always perform a read operation like `getNodeState()` or `getRoot()`.
  - **Using the same builder incorrectly**: After `dispose()`, the `DocumentMK.Builder` may also need to be re-created. Understand the builder lifecycle — some builders can be reused, others cannot. Check the builder's `getNodeStore()` method behavior.
  - **Testing only in isolation**: The bug may only manifest when the cluster node info (e.g., machine ID, instance ID) matches between the disposed and new instance. Ensure the test uses the same cluster configuration.
  - **Forgetting to dispose the second instance**: Always clean up both instances to prevent test pollution.

### Example (correct approach — simulating a restart):

```java
// Get first store
DocumentNodeStore store1 = builder.getNodeStore();
store1.getNodeState(); // sanity check

// Dispose (simulate shutdown)
store1.dispose();

// Re-create store with same configuration (simulate restart)
DocumentNodeStore store2 = builder.getNodeStore();

// Verify the new store is usable
assertNotNull(store2.getNodeState());
assertNotNull(store2.getRoot());

// Clean up
store2.dispose();
builder.dispose();
```

### Example (incorrect approach — does not trigger the bug):

```java
// Only tests a single dispose without re-creation
DocumentNodeStore store = builder.getNodeStore();
store.dispose();
// No new store created — bug may not be detected
```