---
name: branch-reset-conflict-recovery
description: WHEN testing branch reset operations after a merge conflict in a version-controlled
  tree structure, THEN verify that resetting to a pre-conflict ancestor preserves
  nodes added before the conflict while undoing only the conflicting change. Common
  pitfalls include asserting nodes are missing after reset when they should still
  exist.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# branch-reset-conflict-recovery

## Instructions

# Branch Reset Conflict Recovery

## Instructions

WHEN the TG encounters a MicroKernel-style API that supports branching, merging, and reset (`branch`, `merge`, `reset` operations on a revision history) where:

- A branch is created from a base revision
- A conflicting change is made on trunk (e.g., adding a node `/foo` to trunk)
- The same node `/foo` is then added on the branch on top of other valid changes (e.g., first adding `/bar` then adding `/foo`)
- A merge attempt fails with a `MicroKernelException` due to the conflict

THEN the TG should test the following scenario:

1. Create a branch (`b0`) from trunk
2. Make a change on trunk that will conflict (e.g., `addNodes(null, "/foo")`)
3. On the branch, first make a valid non-conflicting change (e.g., `addNodes(b0, "/bar")` → `b1`)
4. On the branch, make a conflicting change on top of the valid one (e.g., `addNodes(b1, "/foo")` → `b2`)
5. Verify merge of `b2` fails with `MicroKernelException`
6. Reset the branch to the revision just before the conflicting change: `mk.reset(b2, b1)` → `b3`
7. Merge the reset branch: `mk.merge(b3, null)` → `rev`
8. **Verify that ALL nodes from the pre-conflict branch state still exist** — specifically the non-conflicting nodes (e.g., `/bar`) AND the nodes that conflicted on trunk (e.g., `/foo` which was added on trunk)

Common pitfalls to avoid:

- **Pitfall: Assuming reset discards all branch changes.** Reset to a pre-conflict revision should revert only changes made *after* that revision. Valid changes made before the conflicting change must be preserved.
- **Pitfall: Testing only that the merge succeeds.** The critical assertion is that nodes created on the branch before the conflict are still present after the reset-and-merge cycle.
- **Pitfall: Forgetting to set up the trunk-side conflicting change.** Without a conflicting change on trunk, the merge won't fail and the reset won't be exercised.
- **Pitfall: Using the wrong target revision for reset.** The reset target must be the last good revision on the branch *before* the conflicting change was added (e.g., `b1`, not `b0`).
- **Pitfall: On a failing buggy implementation**, the reset may produce a revision where nodes from the pre-conflict branch state appear to be missing (e.g., `/foo` does not exist), causing `assertNodesExist` to fail. The test should catch this by asserting existence of those nodes.

### Correct test pattern

```java
@Test
public void resetConflictAddExistingNode() {
    String b0 = mk.branch(null);       // create branch from trunk
    addNodes(null, "/foo");            // conflicting change on trunk
    String b1 = addNodes(b0, "/bar");  // valid change on branch
    String b2 = addNodes(b1, "/foo");  // conflicting change on branch
    try {
        mk.merge(b2, null);
        fail("merge with conflict must fail");
    } catch (MicroKernelException e) {
        // expected
    }
    String b3 = mk.reset(b2, b1);      // reset to pre-conflict revision
    String rev = mk.merge(b3, null);   // merge should now succeed
    // BOTH /foo (from trunk) and /bar (from branch pre-conflict) must exist
    assertNodesExist(rev, "/foo", "/bar");
}
```

### Incorrect test pattern (missing assertions)

```java
@Test
public void resetConflictAddExistingNode_WRONG() {
    String b0 = mk.branch(null);
    addNodes(null, "/foo");
    String b1 = addNodes(b0, "/bar");
    String b2 = addNodes(b1, "/foo");
    try {
        mk.merge(b2, null);
        fail();
    } catch (MicroKernelException e) { }
    String b3 = mk.reset(b2, b1);
    String rev = mk.merge(b3, null);
    // WRONG: Only checking merge succeeded, not checking node existence!
    // Bug: /foo might not exist in rev, but test passes
}
```