---
name: remove-child-node-read-after-remove
description: When testing a tree/builder node-removal method that removes child nodes
  from the parent's internal map but does not update the parent's child-node mapping,
  the test should verify that reading a previously removed child node returns null
  and that re-adding a child with the same name works correctly afterward.
code_tags:
- STATE_TRANSITION
- NULL_CHECK
- RESOURCE_LIFECYCLE
test_pattern: STATE_TEST
---

# remove-child-node-read-after-remove

## Instructions

# Removing a child node must properly invalidate the parent's child node map

## Instructions

- WHEN the TG encounters a `NodeBuilder` (or similar tree/builder pattern) that provides methods like `removeNode(name)` and `getChildNode(name)` on a parent builder that caches or stores child builders internally
- THEN the TG should test `removeNode(name)` followed by reading the same child back via `getChildNode(name)` on the same parent builder, verifying that **the removed child is no longer accessible** and that the parent returns a **newly created child builder** (not a stale reference)
- Concretely, the test should:
  1. Create a root builder
  2. Add a child node via `getChildNode("child")` on the builder (which creates a child builder and stores it)
  3. Call `removeNode("child")` to remove that child
  4. Call `getChildNode("child")` again on the same parent builder
  5. Assert that the result is **not null** (because a new child builder should be created), **but verify its internal state** — e.g., check that it is a fresh builder with no pre-existing properties, or check that it is not equal to the previously removed builder (using `!=` reference comparison or state inspection)
- A common pitfall: only testing that `getChildNode()` returns `null` for a non-existent child, or testing remove-and-read without checking that the parent's internal child map was properly invalidated — the bug is that the parent **still returns the old (removed) child builder** instead of creating a new one
- Example of a **correct** test (targeting the bug):

```java
NodeBuilder root = ...;
// Create a child
NodeBuilder child = root.getChildNode("test");
// Remove it
root.removeNode("test");
// Read it back — the buggy version returns the SAME child (stale reference)
NodeBuilder childAfterRemove = root.getChildNode("test");
// The fixed version should return a DIFFERENT builder (fresh child)
assertNotNull(childAfterRemove);
assertNotSame(child, childAfterRemove);
// Optionally verify the fresh child has no properties
assertFalse(childAfterRemove.getPropertyNames().iterator().hasNext());
```

- Example of an **incorrect** test (would NOT catch this bug):

```java
NodeBuilder root = ...;
root.getChildNode("test");
root.removeNode("test");
// This only checks that removeNode succeeds — does NOT verify the re-read behavior
// A buggy implementation could pass this
assertTrue(true);
```

- Additional guidance: If the root builder's `getChildNode()` method has a parameter (like a `String` name), test with the **same name** that was used to create and then remove the child — the bug is triggered when the removed child's name is reused