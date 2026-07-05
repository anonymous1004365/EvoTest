---
name: path-deletion-ordered-gc
description: When deleting documents by path, the collection must be sorted in reverse-depth
  order so that child paths are deleted before their parents. Without this ordering,
  a parent deletion can fail leaving an orphaned child, or cause an inconsistent state.
  Use this skill when testing code that removes items by path and depends on deletion
  order.
code_tags:
- ORDER_DEPENDENCY
- STATE_MUTATION
test_pattern: STATE_TEST
---

# path-deletion-ordered-gc

## Instructions

# Path Deletion Must Be Ordered by Depth (Children Before Parents)

## Instructions

- WHEN the TG encounters code that collects paths/IDs into a `List<String>` and then calls a bulk `remove(Collection, List)` operation (e.g., `nodeStore.getDocumentStore().remove(Collection.NODES, docIdsToDelete)`)
- THEN the TG should verify that the list is **sorted by path depth in descending order** (deepest paths first) before the remove call, so that children are deleted before their parents
- WHEN a deletion fails partway through (e.g., an exception is thrown after deleting some items), THEN the remaining items should still satisfy the invariant that no child paths exist without their parent — this requires that children appear before their parents in the deletion list
- The TG should test with a list containing paths of varying depth, such as `"1:/x"` and `"2:/x/y"`, and verify that after a partial failure and retry, both the child and parent nodes are properly removed
- Common pitfalls:
  - Testing only with single-depth paths (e.g., only `"/x"`, `"/y"`) which masks ordering bugs
  - Forgetting that `PathComparator.INSTANCE` sorts by **depth descending** then **string ascending** — using the wrong comparator can reverse the order
  - Assuming that `Collections.sort()` is called when it may be missing from some code paths (e.g., the buggy version of `VersionGarbageCollector.collectDeletedDocuments()` did NOT call `Collections.sort(docIdsToDelete, PathComparator.INSTANCE)`, while the fixed version does)

**Correct approach:**
```java
// After collecting docIdsToDelete, sort so deepest paths come first
Collections.sort(docIdsToDelete, PathComparator.INSTANCE);
// Then remove in batch
nodeStore.getDocumentStore().remove(Collection.NODES, docIdsToDelete);
```

**Incorrect approach (buggy):**
```java
// Missing the sort — parents may be deleted before children
nodeStore.getDocumentStore().remove(Collection.NODES, docIdsToDelete);
// If deletion is interrupted after removing /x but before removing /x/y,
// /x/y becomes an orphan
```