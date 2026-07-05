---
name: empty-node-state-equals-modification
description: When a class wraps or delegates to another NodeState implementation (e.g.,
  EmptyNodeState, ModifiedNodeState), equals()/hashCode() must be overridden to correctly
  handle comparisons between different wrapper types. Use this skill when testing
  NodeState subclasses that delegate property/child iteration to a base state.
code_tags:
- STATE_MUTATION
- EQUALS_HASHCODE
test_pattern: STATE_TEST
---

# empty-node-state-equals-modification

## Instructions

# Empty NodeState equals() After Modification

## Instructions

- WHEN the TG encounters a `NodeState` implementation that delegates `getChildNodeEntries()`, `getProperties()`, or `compareAgainstBaseState()` to another `NodeState` (e.g., `EmptyNodeState.EMPTY`), and the class represents a wrapper/modified view of that base state (e.g., `EmptyNodeState`, `ModifiedNodeState`)
- THEN the TG should test that the `equals()` method is properly overridden so that two instances representing the same logical empty state (e.g., two `EmptyNodeState` instances) are equal, even after one has been "modified" (i.e., wrapped) by another `NodeState` implementation
- Specifically: create a `NodeState` by modifying another (e.g., `x = EmptyNodeState.EMPTY.builder().build()`) and verify that `x.equals(EmptyNodeState.EMPTY)` returns `true`. The test should assert equality and **not** rely on `compareAgainstBaseState` as a proxy for equality, since `compareAgainstBaseState` may remain `null`/empty while `equals()` can return `false` due to class mismatch
- Common pitfalls: 
  - Testing only `compareAgainstBaseState()` instead of `equals()` — the bug was that `equals()` returned `false` because the class comparison (`getClass() != other.getClass()`) failed when comparing across `EmptyNodeState` and `ModifiedNodeState` instances that both represent an empty state, even though `compareAgainstBaseState()` showed no differences
  - Testing equality only between two `EmptyNodeState.EMPTY` singletons — the bug only manifests when one side is a `ModifiedNodeState` wrapping `EMPTY`
  - Assuming that because `compareAgainstBaseState()` returns a `null` (empty) result, `equals()` will also return `true`

### ✅ Correct Approach (catches the bug)
```java
@Test
public void missingEqualsModified() {
    // Modify EMPTY to get a ModifiedNodeState wrapping EMPTY
    NodeState modified = EmptyNodeState.EMPTY.builder().build();
    // This should be equal to EMPTY since no actual modifications were made
    assertEquals("Modified empty state should be equal to EmptyNodeState.EMPTY", 
                 EmptyNodeState.EMPTY, modified);
}
```

### ❌ Incorrect Approach (misses the bug)
```java
@Test
public void compareAgainstBaseState() {
    // This test would pass even on the buggy version because
    // compareAgainstBaseState() returns null (no differences)
    assertNull(EmptyNodeState.EMPTY.compareAgainstBaseState(
        EmptyNodeState.EMPTY.builder().build()));
}
```