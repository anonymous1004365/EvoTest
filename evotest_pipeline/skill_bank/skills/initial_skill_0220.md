---
name: nodebuilder-setnode-consistency
description: When testing MemoryNodeBuilder.setNode(), verify that a previously removed
  child node builder is properly reconnected after setNode() and correctly reflects
  the new child node state. Use this skill when encountering builders that operate
  on child nodes after remove-then-setNode operations.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# nodebuilder-setnode-consistency

## Instructions

# MemoryNodeBuilder setNode Consistency Test

## Instructions

- WHEN the TG encounters code that modifies a `MemoryNodeBuilder` (or `NodeBuilder`) by removing a child node and then calling `setNode()` on it, or where a child builder obtained via `getChildNode()` is used after its parent has been manipulated with `setNode()`
- THEN the TG should write a test that:
  1. Creates a `NodeBuilder` from a known base `NodeState` (e.g., `EMPTY_NODE.builder()` or any non-empty `NodeState`)
  2. Obtains a child builder via `builder.getChildNode("someName")` 
  3. Removes that child node via the parent (e.g., `builder.getChildNode("someName").remove()`)
  4. Replaces the child node via `builder.setNode("someName", newNodeState)` where `newNodeState` is e.g., `EMPTY_NODE` or a `NodeState` with specific properties
  5. Validates that a subsequent call to `builder.getChildNode("someName")` returns a builder that correctly reflects the newly set node's state — specifically, that property modifications made on the new child builder are visible through previously obtained builder references
  6. Expects that on the **buggy** version, the old builder reference may still see stale/broken state after `setNode()`, causing an `IllegalStateException` when trying to use it, or returning incorrect property values

- Common pitfalls to avoid:
  - Testing only `setNode()` without first removing the node — the bug manifests specifically when a removed node is then set again
  - Obtaining a fresh child builder instead of reusing the old builder reference — the old reference is where the stale state bug appears
  - Not checking that the old child builder's `getChildNodeCount()` or `hasProperty()` calls return correct values after the parent's `setNode()`
  - Forgetting to verify both the old reference AND a new reference from the parent

### Example (Correct)

```java
@Test
public void testSetNodeAfterRemove() {
    NodeBuilder root = EMPTY_NODE.builder();
    root.child("test");
    root.getChildNode("test").remove();
    
    // Old builder reference — may be stale on buggy version
    NodeBuilder testBuilder = root.getChildNode("test");
    assertFalse(testBuilder.exists());  // removed
    
    // setNode replaces the child
    root.setNode("test", EMPTY_NODE);
    
    // On the fixed version, the old builder reference should reconnect
    // On the buggy version, this might throw IllegalStateException
    // or return stale state
    int childCount = testBuilder.getChildNodeCount(1);
    assertEquals(0, childCount);
    
    // Verify through a new reference too  
    NodeBuilder newTestBuilder = root.getChildNode("test");
    assertTrue(newTestBuilder.exists());
    assertEquals(0, newTestBuilder.getChildNodeCount(1));
}
```

### Example (Incorrect)

```java
// INCORRECT: Doesn't test the old builder reference
@Test
public void testSetNode() {
    NodeBuilder root = EMPTY_NODE.builder();
    root.child("test");
    root.getChildNode("test").remove();
    root.setNode("test", EMPTY_NODE);
    
    // Only tests a fresh reference — misses the bug
    assertTrue(root.getChildNode("test").exists());
}
```