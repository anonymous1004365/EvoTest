---
name: unmodified-builder-state-equals-base
description: When obtaining a child NodeBuilder from the parent via `child()` or `getChildNode()`
  and making zero modifications to it or its subtree, `getNodeState()` must equal
  `getBaseState()`. This skill catches bugs where internal builder state tracking
  (e.g., UnconnectedHead vs ConnectedHead transitions) incorrectly inherits modified
  children from sibling builders.
code_tags:
- NODE_STATE_BUILDER_EQUALS_BASE
- STATE_MUTATION
test_pattern: STATE_TEST
---

# unmodified-builder-state-equals-base

## Instructions

# Unmodified Builder State Equals Base State

## Instructions

- WHEN the code under test is a `NodeBuilder` implementation (e.g., `MemoryNodeBuilder`) and you obtain a child builder via `root.child("x")` or `root.getChildNode("x")` without making any modifications to that child or its subtree
- THEN the test MUST assert that `childBuilder.getNodeState()` equals `childBuilder.getBaseState()` using `assertEquals(childBuilder.getBaseState(), childBuilder.getNodeState())` — this invariant must hold even if a sibling child builder obtained via a separate call to `root.child("x")` has been modified (e.g., by adding a child node like `sibling.child("q")`)
- The test MUST use `assertEquals` from `junit.framework.Assert` to compare the two `NodeState` objects, which relies on `AbstractNodeState.equals()` for deep structural comparison
- Common pitfalls to avoid:
  1. Testing only the root builder — the bug manifests specifically on child builders obtained via `child()` or `getChildNode()`
  2. Assuming sibling builder modifications don't affect the unmodified builder's `getNodeState()` — the bug is that a sibling builder's modifications (e.g., adding child "q") can leak into the unmodified builder's `getNodeState()` while not affecting `getBaseState()`
  3. Not testing with both raw `NodeState` and `ModifiedNodeState.squeeze(base)` base states — the bug appears with both but especially with `ModifiedNodeState.squeeze()` wrapped base states
  4. Using `assertTrue(childBuilder.getNodeState().equals(childBuilder.getBaseState()))` — use `assertEquals` which gives a clearer failure message

### Correct Example

```java
@Test
public void testUnmodifiedEqualsBase() {
    NodeBuilder root = base.builder();
    NodeBuilder x = root.child("x");
    assertEquals(x.getBaseState(), x.getNodeState());
}
```

### Incorrect Example (would NOT catch the bug)

```java
@Test
public void testUnmodifiedEqualsBase_Bad() {
    NodeBuilder root = base.builder();
    NodeBuilder x = root.child("x");
    // Missing: assertion that getNodeState() == getBaseState()
    // or using assertTrue instead of assertEquals
    // or only testing the root builder
    assertTrue(root.getNodeState().equals(root.getBaseState()));
}
```