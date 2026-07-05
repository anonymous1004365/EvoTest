---
name: concurrent-child-order-race
description: When trees have orderable children and concurrent addChild operations
  create ordering conflicts, test that child ordering metadata is correctly resolved.
  Apply this skill when orderable child nodes are added concurrently without conflict
  handling for the ordering property.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# concurrent-child-order-race

## Instructions

# Concurrent Child Ordering Conflict Test

## Instructions

- WHEN the TG encounters a `Tree` implementation that supports `orderable` children (where children maintain a defined order via an ordering property like `:childOrder`), and concurrent `addChild()` operations can happen from multiple threads
- THEN the TG should write a test that:
  - Creates a parent node with orderable children
  - Adds child nodes concurrently from multiple threads (e.g., using a `ThreadPoolExecutor` or manually starting threads)
  - Verifies that after all threads complete, all expected children are present **and** their order matches the expected sequence (e.g., `[node1, node2, node3, node4]`)
  - Specifically, the test should check that the rendering of child order (via `getChildOrder()`, `getOrderableChildren()`, or iterating children in order) returns exactly all children in the correct order, even under concurrent add-and-commit scenarios
  - Use `CountDownLatch` or `CyclicBarrier` to coordinate thread start times and ensure true concurrency, not just sequential addition

- Common pitfalls to avoid:
  - Testing only sequential child addition, which misses the race condition entirely
  - Testing only that children exist (presence check) without verifying their **order** — the bug manifests as a missing child in the ordering metadata, not as a missing child node
  - Using `Thread.sleep()` for timing coordination; always use proper concurrency primitives (`CountDownLatch`, `CyclicBarrier`)
  - Only testing with a single child, which cannot expose ordering conflicts
  - Forgetting to commit after each addChild in a way that triggers the conflict handler

- Correct example:
```java
// Parent is orderable. Add child1, child2, child3 sequentially first.
// Then concurrently add child4 from one thread and do nothing unusual from another.
// After all threads join, assert the ordered children list equals [node2, node1, node3, node4].
// The buggy code would produce [node2, node1, node3] (missing node4 from ordering).
```

- Incorrect example (would not catch the bug):
```java
// Adding all children sequentially in a single thread — this always works
// because there's no concurrent ordering conflict to trigger the missing metadata.
```