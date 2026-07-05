---
name: memory-node-builder-reset-state-invalidation
description: Teaches how to test that resetting a MemoryNodeBuilder properly invalidates
  child builder cached state, preventing stale/stuck state after rebase. Applies when
  child builders cache parent state and need to be cleared on parent reset.
code_tags:
- STATE_MUTATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# memory-node-builder-reset-state-invalidation

## Instructions

# MemoryNodeBuilder State Invalidation on Reset

## Instructions

- WHEN the TG encounters a `MemoryNodeBuilder` (or similar tree-structured builder) that has child builders caching a reference to the parent's base state (e.g., an `AbstractPropertyState` or `MutableNodeState`), and the parent's `baseState` field can be replaced via a `reset(NodeState)` call
- THEN the TG should write a test that:
  1. Creates a root `MemoryNodeBuilder` and adds at least one child builder via `child(name)`.
  2. Calls `reset()` on a parent builder (e.g., the root or an intermediate node) to replace its base state with a new `NodeState`.
  3. After the reset, attempts to read child properties or child state from a *child* builder that previously cached the parent's base state (e.g., a child builder that was obtained before the reset).
  4. Verifies that the child builder's state is properly invalidated after the parent reset — specifically, that the child builder does NOT continue holding a stale reference to the old parent base state (which could cause a `NullPointerException` or return stale data).
- The test should verify that the child builder's internal cached base state reference is either `null` after the parent reset, or is re-derived from the parent's new base state, depending on the expected behavior of `getBaseState()`.
- **Concretely**: after parent.reset(newState), assert that child.getBaseState() returns the new state (not the old one), or that child methods accessing the child's own base state do not throw NullPointerException.
- **Common pitfalls**:
  - Testing only the root builder's reset behavior without checking its children's cached state.
  - Assuming that resetting a parent automatically propagates to already-obtained child builders without explicit invalidation logic.
  - Testing only with no children present, missing the case where a child builder holds a direct reference to parent's old internal state field.
  - Only calling `getNodeState()` at the end and not checking intermediate internal state.

**Example (correct — catches stale state bug):**
```java
@Test
public void testResetInvalidatesChildState() {
    MemoryNodeBuilder rootBuilder = new MemoryNodeBuilder(nodeState);
    MemoryNodeBuilder childBuilder = (MemoryNodeBuilder) rootBuilder.child("a");

    // Initially child should have valid state
    assertNotNull(childBuilder.getBaseState());

    // Reset root with new base state
    rootBuilder.reset(nodeState2);

    // After parent reset, child's cached state should be invalidated
    // Assert that child no longer refers to old parent state
    // (If fix exists, child.getBaseState() returns new state or null;
    //  if buggy, it may hold stale reference and cause NPE)
    NodeState childBase = childBuilder.getBaseState();
    assertNotNull("Child should have valid state after parent reset", childBase);
    assertEquals(newPropertyValue, childBase.getProperty("someProp"));
}
```

**Example (incorrect — misses the bug):**
```java
@Test
public void testResetRootOnly() {
    MemoryNodeBuilder rootBuilder = new MemoryNodeBuilder(nodeState);
    rootBuilder.reset(nodeState2);
    // Only testing root reset, no child builder involved
    assertEquals(nodeState2, rootBuilder.getNodeState());
    // Bug is only triggered when a child builder was obtained BEFORE reset
}
```