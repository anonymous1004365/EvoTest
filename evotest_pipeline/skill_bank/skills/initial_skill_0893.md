---
name: node-get-nodes-size-consistency
description: When a Node.getNodes() method iterates over child nodes, the returned
  iterator's size and the actual iteration count must match. This skill catches bugs
  where an internal counter (e.g., a read position) is corrupted by failed operations,
  causing hasNext() to return false prematurely while size() still reports a positive
  count.
code_tags:
- RESOURCE_MANAGEMENT
- BOUNDARY_CHECK
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# node-get-nodes-size-consistency

## Instructions

# Node getNodes Size Consistency After Failed Operations

## Instructions

- WHEN the TG encounters code that iterates over child nodes of a JCR Node using an internal state-based iterator (e.g., a `Pointer` or position counter that is incremented during iteration and potentially corrupted by failed `getChild` operations)
- THEN the TG should write a test that:
  1. Creates a node with multiple child nodes (e.g., at least 3 children)
  2. Iterates through all children using `getNodes()`, verifying that `iterator.hasNext()` returns `true` for each expected child and that the total number of iterated children matches `iterator.getSize()` (or equivalent size method)
  3. Specifically, after some children have been successfully iterated, performs an operation that fails (e.g., calls `node.getNodes()` on a non-existent relative path) which would corrupt the internal pointer, then verifies that the remaining children can still be iterated and the size remains consistent
  4. Asserts that the iteration completes without prematurely stopping, and that `getSize()` returns the correct count of remaining children after the failed operation
- The test should expect that on the buggy version, `hasNext()` returns `false` prematurely (before all children are visited) while `size()` still returns a positive number, causing the test to detect the discrepancy
- Common pitfalls: The TG might only test the normal case without a failing operation, or might test the failing operation without verifying that subsequent iteration still works correctly. The TG might also rely on `getSize()` returning `-1` (which can happen on a corrupted state) without checking that this signals an error. The correct behavior is that `getSize()` returns the actual number of remaining children AND `hasNext()` returns `true` for each remaining child.

### Example (Correct Test):
```java
// Given: a node "testNode" with children "child1", "child2", "child3"
NodeIterator it = session.getNode("/testNode").getNodes();
assertEquals(3, it.getSize());
assertTrue(it.hasNext());
Node firstChild = (Node) it.next();
assertEquals("child1", firstChild.getName());

// Simulate a failed operation that might corrupt internal state
NodeIterator innerIt = firstChild.getNodes(); // child1 has no children
assertFalse(innerIt.hasNext()); // OK

// Now verify remaining children of parent are still accessible
assertEquals(2, it.getSize()); // Should be 2 remaining
assertTrue(it.hasNext()); // Buggy version returns false here prematurely
Node secondChild = (Node) it.next();
assertEquals("child2", secondChild.getName());
assertTrue(it.hasNext());
Node thirdChild = (Node) it.next();
assertEquals("child3", thirdChild.getName());
assertFalse(it.hasNext());
assertEquals(0, it.getSize());
```

### Example (Incorrect Test — misses the bug):
```java
// This test doesn't trigger the bug because it doesn't corrupt the pointer
NodeIterator it = session.getNode("/testNode").getNodes();
assertEquals(3, it.getSize());
int count = 0;
while (it.hasNext()) {
    it.next();
    count++;
}
assertEquals(3, count); // Works on both buggy and fixed versions
```