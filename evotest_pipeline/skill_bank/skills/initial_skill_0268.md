---
name: hidden-path-query-suppression-in-commit-hooks
description: When a commit hook processes nodes and traverses the node tree (e.g.,
  via compareAgainstBaseState or a diff), hidden paths (starting with ":") in the
  node tree must not be queried from the document store. This skill helps prevent
  tests from exposing queries for hidden paths that should be skipped.
code_tags:
- VALIDATION
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# hidden-path-query-suppression-in-commit-hooks

## Instructions

# Hidden Path Query Suppression in Commit Hooks

## Instructions

- WHEN the TG encounters a commit hook (implementing `CommitHook`) that traverses node states by diffing (`compareAgainstBaseState` with a `DefaultNodeStateDiff`) or by iterating child nodes
- THEN the TG must test that the hook correctly skips hidden paths (paths/names starting with `:` such as `:hidden`) when performing operations that would trigger queries against the underlying document store
  - Create a scenario where a hidden node (e.g., `:hidden`) with `MANY_CHILDREN_THRESHOLD + 1` children exists under the root
  - Use a custom `DocumentStore` wrapper (extending `MemoryDocumentStore`) that overrides `query()` to record all queried paths from any indexed query (when `indexedProperty != null`)
  - Before executing the commit hook, clear the recorded paths set
  - After `processCommit()` returns, assert that the recorded paths set is empty: `assertEquals("Must not query for hidden paths: " + paths.toString(), 0, paths.size())`
  - Ensure enough modifications happen on another branch (e.g., via `foo.setProperty("p", "v"); foo.removeProperty("p");`) so that a new branch revision is created, making the hidden node's children trigger an indexed query from the document store
  - The key boundary condition: create exactly `MANY_CHILDREN_THRESHOLD + 1` children under the hidden node (`DocumentMK.MANY_CHILDREN_THRESHOLD` defaults to 50)

- Common pitfalls to avoid:
  - **Not creating enough children**: Testing with fewer than `MANY_CHILDREN_THRESHOLD + 1` children under the hidden node will not trigger the bug — the indexed query path may not be hit
  - **Not triggering a branch creation**: Without adding enough changes to force creation of a new branch revision (by toggling a property on a visible node like `foo`), the hidden node's children may not trigger a query against the document store
  - **Testing only the hook in isolation without setting up a realistic document store state**: The hook must run against a live `DocumentNodeStore` with actual revisions
  - **Forgetting to clear the paths set before hook invocation**: Previous query calls may have already recorded paths

### Correct approach example:
```java
// Create hidden node with enough children
builder.child(":hidden");
ns.merge(builder, ...);
builder = ns.getRoot().builder();
NodeBuilder hidden = builder.child(":hidden");
for (int i = 0; i <= DocumentMK.MANY_CHILDREN_THRESHOLD; i++) {
    hidden.child("child-" + i);
}
// Force branch creation
NodeBuilder foo = builder.child("foo");
while (getRevisionsSize(store, "/") == numRevs) {
    foo.setProperty("p", "v");
    foo.removeProperty("p");
}
store.paths.clear();
// Execute hook
hook.processCommit(ns.getRoot(), builder.getNodeState(), ...);
// Verify no queries for hidden paths
assertEquals("Must not query for hidden paths: " + store.paths, 0, store.paths.size());
```

### Incorrect approach (would miss the bug):
```java
// Only 1 child — too few to trigger indexed query
builder.child(":hidden").child("only-child");
ns.merge(builder, ...);
// No branch creation — hook may skip hidden traversal
hook.processCommit(...);
assertTrue(store.paths.isEmpty()); // Passes even with bug present!
```