---
name: hidden-node-validation-on-commit
description: When a commit contains operations that add nodes under hidden (internal)
  paths, the validator must explicitly check the path and reject the operation. This
  skill teaches how to test that hidden/internal nodes are properly rejected during
  commit validation while visible counterparts are allowed.
code_tags:
- VALIDATION
- STATE_MUTATION
- HIDDEN_NODE_VALIDATION
test_pattern: STATE_TEST
---

# hidden-node-validation-on-commit

## Instructions

# Hidden Node Validation on Commit

## Instructions

- WHEN the TG encounters a validator class that rejects operations on hidden/internal nodes (e.g., nodes under paths starting with `":hidden"`, internal namespaces, or JCR system paths like `"jcr:system"`)
- THEN it should verify that when a commit adds, modifies, or removes a node under a hidden path, the validator throws a `CommitFailedException` with an appropriate constraint violation (e.g., access control constraint violation). The TG should test at least two code paths:
  1. A test where a node is added under a visible (non-hidden) path — this should **succeed** (no exception).
  2. A test where the same type of node is added under a hidden/internal path — this should **fail** with a `CommitFailedException`.
- The test must create a `Root` from the `ContentRepository`, obtain a `ContentSession`, and use `Tree` operations (or `NodeState` mutations) to simulate the commit. The validator under test must be registered in the commit validation chain for the test context.
- Verify the specific exception type: `CommitFailedException` must be thrown. If the validator is for access control, the constraint violation should be of type access control (`ConstraintViolation.ACCESS_CONTROL`).
- Common pitfalls to avoid:
  - Testing only the visible path and assuming the hidden path works the same way — this misses the bug entirely.
  - Forgetting to set up the proper `Root`/`ContentSession` context so the validator is actually invoked.
  - Not including a baseline test (visible path succeeds) so it's unclear whether the test infrastructure is correct.
  - Testing the validator in isolation (unit test) without the full commit infrastructure — the bug may only manifest during actual commit validation.

### Correct Example (Java, JUnit 4):

```java
// Correct: tests both visible (should succeed) and hidden (should fail) paths
@Test
public void hiddenNodeAdded() throws CommitFailedException {
    ContentSession cs = root.getContentSession();

    // Visible path test — should succeed
    Tree visibleTree = root.getTree("/");
    visibleTree.addChild("testNode");
    visibleTree.getChild("testNode").setProperty("jcr:primaryType", "nt:unstructured");
    root.commit();
    root.refresh();

    // Hidden path test — should fail
    Tree hiddenTree = root.getTree("/");
    hiddenTree.addChild(":hiddenNode");
    hiddenTree.getChild(":hiddenNode").setProperty("jcr:primaryType", "rep:ACL");
    assertThrows(CommitFailedException.class, () -> root.commit());
}
```

### Incorrect Example:

```java
// Incorrect: only tests visible path, misses the bug entirely
@Test
public void hiddenNodeAdded() throws CommitFailedException {
    ContentSession cs = root.getContentSession();
    Tree tree = root.getTree("/");
    tree.addChild("testNode");
    tree.getChild("testNode").setProperty("jcr:primaryType", "nt:unstructured");
    root.commit();  // This succeeds, but doesn't test hidden paths at all
}
```

### Another Incorrect Example:

```java
// Incorrect: no baseline visible-path test, so a false positive is possible
@Test
public void hiddenNodeAdded() throws CommitFailedException {
    Tree hiddenTree = root.getTree("/");
    hiddenTree.addChild(":hiddenNode");
    assertThrows(CommitFailedException.class, () -> root.commit());
    // Without a visible path test, if the validator rejects ALL nodes, this test still passes
}
```