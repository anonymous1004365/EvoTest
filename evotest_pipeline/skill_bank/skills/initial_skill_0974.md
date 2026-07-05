---
name: removed-node-state-mutation
description: When a node builder gets removed from its parent, further state mutation
  operations like reading properties should throw an IllegalStateException. This skill
  helps write tests that verify operations on removed/invalidated builders correctly
  throw.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# removed-node-state-mutation

## Instructions

# Removed Node Builder State Validation

## Instructions

- WHEN the TG encounters a class that implements a node builder pattern (e.g., `MemoryNodeBuilder`) where a builder node can be removed from its parent via a `remove()` method
- THEN the TG should test that operations on a removed builder throw an `IllegalStateException`. Specifically:
  1. Create a root builder, add a child node to it, get a reference to the child builder
  2. Call `remove()` on the child builder (from the parent's perspective, e.g., `getParent().remove()` if the child has a `getParent()` method, or just call `remove()` directly if it removes itself from the parent)
  3. Try to read or mutate state on the removed builder node (e.g., `setProperty(...)`, `getPropertyState(...)`, `getNodeState()`, `addChild(...)`, `child(...)`, `getName()`, or other state-reading operations)
  4. Assert that an `IllegalStateException` is thrown by wrapping the operation in `assertThrows(IllegalStateException.class, () -> ...)`

- Common pitfalls to avoid:
  - Testing only `remove()` itself and not the subsequent operations on the removed node
  - Forgetting that the node should throw on ALL state-mutating or state-reading operations after removal, not just on `setProperty`
  - Assuming that a removed node silently becomes a no-op — it should fail fast with `IllegalStateException`
  - Testing on the parent instead of on the removed child builder reference

- Correct example:
```java
// Create a root builder, add a child, remove it, then verify operations throw
MemoryNodeBuilder rootBuilder = new MemoryNodeBuilder(new RootFactory());
rootBuilder.child("child");
MemoryNodeBuilder child = (MemoryNodeBuilder) rootBuilder.getChild("child");
child.remove();
assertThrows(IllegalStateException.class, () -> child.setProperty("test", "value"));
assertThrows(IllegalStateException.class, () -> child.getNodeState());
```

- Incorrect example:
```java
// ❌ Only tests remove() itself, not state access after removal
MemoryNodeBuilder rootBuilder = new MemoryNodeBuilder(new RootFactory());
rootBuilder.child("child");
// just calls remove — doesn't verify state access after removal throws
rootBuilder.getChild("child").remove();
assertTrue(true); // doesn't test the post-removal behavior
```