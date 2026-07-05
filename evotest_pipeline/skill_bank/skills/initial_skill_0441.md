---
name: move-before-remove-concurrentmodification
description: When a mutable tree node is moved and then the move source is removed,
  test that the remove operation does not throw ConcurrentModificationException. This
  skill applies to tree-structured collections where move operations affect pending
  change tracking.
code_tags:
- COLLECTION_OPERATIONS
- STATE_MUTATION
- VALIDATION
- COLLECTION_ITERATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# move-before-remove-concurrentmodification

## Instructions

# Move-Before-Remove ConcurrentModification in Tree Operations

## Instructions

- WHEN the TG encounters code where a node is moved (via `Tree.move(source, dest)`) and then the **source node** of that same move is subsequently removed (via `Tree.remove()`), and the test target exposes a `commit()` or rebase operation that processes pending changes
- THEN the TG should write a test that:
  1. Creates a root node with a child node (e.g., `child` under `/parent/child`)
  2. Moves that child node to a new location (e.g., `Tree.move("/parent/child", "/parent/moved")`)
  3. Gets the **source tree** at the original path (e.g., `root.getTree("/parent/child")`) and calls `remove()` on it
  4. Calls `root.commit()` and asserts that no `ConcurrentModificationException` or `IllegalStateException` is thrown and the operation succeeds
- The test must verify that after these operations:
  - The moved node exists at the destination path
  - The source path no longer exists
  - The commit completes without throwing a `ConcurrentModificationException`
- **Common mistakes to avoid**:
  - Testing only the move operation without the subsequent remove
  - Testing only the remove without the preceding move — the bug manifests specifically due to the **interaction** between move and remove on the same pending change set
  - Forgetting to call `commit()` — the exception may only surface when pending changes are processed
  - Using the destination tree reference instead of the source tree reference for the remove call

### Correct Example (catches the bug):
```java
@Test
public void removeMoved() throws CommitFailedException {
    ContentRepository repo = new ContentRepositoryImpl(...);
    ContentSession session = repo.login(null, null);
    Root root = session.getLatestRoot();
    
    Tree parent = root.getTree("/");
    Tree child = parent.addChild("child");
    root.commit();
    
    // Move child from /child to /moved
    root.move("/child", "/moved");
    
    // Now remove the SOURCE path (the original /child)
    Tree source = root.getTree("/child");
    source.remove();
    
    // This commit should NOT throw ConcurrentModificationException
    root.commit();
    
    // Verify correct state
    assertTrue(root.getTree("/moved").exists());
    assertFalse(root.getTree("/child").exists());
}
```

### Incorrect Example (does NOT catch the bug):
```java
@Test
public void removeMoved() throws CommitFailedException {
    ContentRepository repo = new ContentRepositoryImpl(...);
    ContentSession session = repo.login(null, null);
    Root root = session.getLatestRoot();
    
    Tree parent = root.getTree("/");
    Tree child = parent.addChild("child");
    root.commit();
    
    // Only test move, or only test remove — misses the interaction
    root.move("/child", "/moved");
    
    // Missing: remove the source path after move
    
    root.commit(); // This alone works fine
}
```