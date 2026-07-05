---
name: hidden-node-concurrent-merge-conflict
description: When performing concurrent merges across cluster nodes, operations on
  hidden nodes (prefixed with ":") can cause merge conflicts (OakMerge0004). Tests
  should verify that hidden child nodes added/modified on one cluster node do not
  conflict with operations on another.
code_tags:
- NULL_CHECK
- RESOURCE_MANAGEMENT
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# hidden-node-concurrent-merge-conflict

## Instructions

# Hidden Node Concurrent Merge Conflict Detection

## Instructions

- WHEN the TG encounters code that merges document node state changes across cluster nodes (e.g., using `DocumentNodeStore.mergeInternalDoc()` or similar merge methods)
- THEN it should test concurrent operations where one cluster node adds or modifies hidden nodes (names prefixed with `":"`) while another cluster node concurrently performs operations on the same parent node
- Specifically, WHEN testing concurrent merges, the TG should:
  - Create two or more cluster node instances sharing the same underlying document store
  - On one cluster node, add/remove/modify hidden child nodes (e.g., nodes named `:dynHidden`)
  - On another cluster node, simultaneously perform operations on the same parent node
  - Verify that the merge does NOT throw `DocumentNodeStoreException` with message containing "OakMerge0004" — this indicates a false conflict where the merge failed due to hidden node changes being incorrectly treated as conflicting
  - If the bug is present, the merge will throw an `OakMerge0004: The node ... was changed in revision(...)` error
- When verifying, test with realistic hidden node names (strings starting with `":"` like `:dynHidden`, `:hidden`, `:status`, etc.)
- Common pitfalls to avoid:
  - Testing only non-hidden node operations — the bug specifically manifests with hidden (colon-prefixed) nodes
  - Using only a single cluster node — the concurrency across cluster nodes is essential to trigger the bug
  - Not checking the specific error message — verify for "OakMerge0004" or "was changed in revision" to confirm the bug
  - Failing to clean up test state between iterations — use proper test setup/teardown

### Example (Correct):
```java
// Correct: Tests concurrent merge across clusters with hidden nodes
// This catches the bug when hidden node changes cause false merge conflicts
DocumentNodeStore ns1 = ...; // cluster node 1
DocumentNodeStore ns2 = ...; // cluster node 2 (same underlying store)

// On ns1: add a hidden node
ns1.getRoot().getChild("test").addChild(":dynHidden");
ns1.merge(...);

// On ns2: concurrently modify the same parent
ns2.getRoot().getChild("test").addChild(":dynHidden", "childWithProp");
// The merge on ns2 should NOT throw OakMerge0004
ns2.merge(...); // <-- would throw on the buggy version
```

### Incorrect (pitfall):
```java
// Wrong: Testing only non-hidden node names
// This would not trigger the bug
ns1.getRoot().getChild("test").addChild("visibleNode");
ns1.merge(...);
ns2.getRoot().getChild("test").addChild("anotherVisibleNode");
ns2.merge(...); // No conflict, bug not detected

// Wrong: Using only one cluster node
ns1.getRoot().getChild("test").addChild(":dynHidden");
ns1.merge(...); // Single node, no concurrency, bug not detected
```