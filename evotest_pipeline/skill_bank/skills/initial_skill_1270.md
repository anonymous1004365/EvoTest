---
name: root-move-children-unaffected-by-commit
description: When testing MutableRoot.move() or commit(), verify that move operations'
  parent-child relationships survive a commit. A commit resets permission providers
  and can invalidate NodeBuilder references, causing moved nodes to lose their children
  on the buggy version.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# root-move-children-unaffected-by-commit

## Instructions

# After a Commit, Moved Trees Should Still Have Their Children

## Instructions

- WHEN the TG is testing a `Root.move(sourcePath, destPath)` operation followed by a `Root.commit()` call
- THEN the TG should verify that after the commit, the moved tree at the destination path still has the same children it had before the move.
  - Specifically, write a test that:
    1. Creates a root tree with a child node (e.g., `x`).
    2. Under `x`, adds a grandchild (e.g., `y`) via `tree.addChild("y")`.
    3. Moves `x` to a new location via `root.move("/x", "/a")`.
    4. Calls `root.commit()`.
    5. Then calls `root.getTree("/a")` and checks that it **has the child `y`**.
    6. Before the commit, the moved tree should already have the child.
  - The bug is that after `commit()`, the `NodeBuilder` reference inside the `MutableTree` becomes stale/invalid because of permission provider reset, so the moved tree appears to have no children.
  - On the buggy version, `root.getTree("/a").hasChild("y")` returns `false` after commit. On the fixed version, it returns `true`.
  - Expected exception/error: **`AssertionError`** from `assertTrue` / `assertEquals` failing because `hasChild("y")` is `false` instead of `true`, or `getChildrenCount(...)` returns 0 instead of 1.

- Common pitfalls:
  - ❌ Testing only the move operation without a commit — the bug only manifests after `commit()` resets internal state.
  - ❌ Testing only the source path after move without verifying children at the destination.
  - ❌ Forgetting to call `root.commit()` before checking the moved tree's children.
  - ❌ Testing a top-level node with no children — the bug is about children being lost, so the test must establish child nodes before the move.

### Correct example (detects the bug):
```java
@Test
public void testMoveChildrenSurviveCommit() throws Exception {
    MutableTree rootTree = root.getTree("/");
    rootTree.addChild("x");
    rootTree.getChild("x").addChild("y");

    assertTrue("x should have child y before move", rootTree.getChild("x").hasChild("y"));

    root.move("/x", "/a");
    assertTrue("Moved /a should have child y before commit",
               root.getTree("/a").hasChild("y"));

    root.commit();

    // BUG: on the buggy version, this assertion FAILS!
    assertTrue("Moved /a should still have child y after commit",
               root.getTree("/a").hasChild("y"));
}
```

### Incorrect example (does NOT detect the bug):
```java
@Test
public void testMoveSuccess() throws Exception {
    MutableTree rootTree = root.getTree("/");
    rootTree.addChild("x");
    assertTrue(root.move("/x", "/a"));       // Only tests move returns true
    root.commit();
    assertTrue(root.getTree("/a").exists());  // Only tests tree exists after commit
    // Missing: check that children of the moved node survived the commit!
}
```