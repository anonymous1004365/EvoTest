---
name: reset-branch-collision-cleanup
description: WHEN a branch is reset (via DocumentMK.reset()) after merge conflicts
  created collision markers, THEN the test must verify that all stale collision markers
  on ancestor documents are properly removed. This skill applies to testing DocumentNodeStore's
  reset operation with conflict scenarios.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# reset-branch-collision-cleanup

## Instructions

# Reset Branch Collision Marker Cleanup

## Instructions

WHEN the TG encounters a test for `DocumentMK.reset(String branchRevisionId, String newBaseRevisionId)` that involves scenarios where:
1. Multiple commits were made on a branch (using `mk.commit()` or `addNodes()`)
2. The same changes were made on trunk, creating merge conflicts
3. `try { mk.merge(branchRev, null); fail("expected"); } catch (DocumentStoreException e) {}` triggers the conflict
4. The branch is then reset with `mk.reset(branchRev, newBaseRev)` to a point before conflicting commits

THEN the TG MUST verify that collision markers (`NodeDocument.COLLISIONS`) on ancestor documents (like the root document at path `/`) are properly cleaned up after the reset. Specifically:

1. **Before reset**: After creating collisions (by committing conflicting changes on trunk), retrieve the root document via `store.find(NODES, getIdFromPath("/"))` and check `doc.getValueMap(COLLISIONS)`. Assert that the map contains entries for the conflicting revisions (size > 0).

2. **After reset**: After calling `mk.reset(branchRev, newBaseRev)` followed by additional commits on the cleaned branch, retrieve the root document again and assert `collisions.size() == 0`.

3. **Use concrete types**: Access the store via `mk.getDocumentStore()`, find documents via `store.find(Collection.NODES, getIdFromPath("/"))`, and check collision maps via `doc.getValueMap(NodeDocument.COLLISIONS)` returning `Map<Revision, String>`.

**Common pitfalls:**
- Testing only that the merge fails after conflict, without checking that reset cleans up collision bookkeeping
- Checking collision markers only on leaf/changed documents but missing ancestor documents (like the root document at `/`)
- Confusing `getLocalMap(COLLISIONS)` (in-memory only) with `getValueMap(COLLISIONS)` (persisted in store)
- Forgetting to re-fetch the document from the store after reset (the local reference is stale)
- Not asserting the collision count is exactly 0 after reset — a single leftover collision marker indicates the bug

**Example (correct approach):**
```java
@Test
public void resetMultipleCommits() {
    DocumentStore store = mk.getDocumentStore();
    
    addNodes(null, "/foo");
    String b0 = mk.branch(null);
    String b1 = mk.commit("", "^\"/foo/p1\":1", b0, null);
    String b2 = mk.commit("", "^\"/foo/p2\":1", b1, null);
    String b3 = mk.commit("", "^\"/foo/p3\":1", b2, null);
    // create collision markers
    mk.commit("", "^\"/foo/p2\":1^\"/foo/p3\":1", null, null);

    NodeDocument rootDoc = store.find(NODES, getIdFromPath("/"));
    Map<Revision, String> collisions = rootDoc.getValueMap(COLLISIONS);
    assertEquals(2, collisions.size()); // markers present before reset

    try {
        mk.merge(b3, null);
        fail("DocumentStoreException expected");
    } catch (DocumentStoreException expected) {}

    String b4 = mk.reset(b3, b1);  // reset back to b1
    String b5 = mk.commit("", "^\"/foo/p4\":1", b4, null);

    rootDoc = store.find(NODES, getIdFromPath("/"));
    collisions = rootDoc.getValueMap(COLLISIONS);
    assertEquals(0, collisions.size()); // markers cleaned up after reset

    String rev = mk.merge(b5, null);
    assertPropExists(rev, "/foo", "p1");
    assertPropExists(rev, "/foo", "p2");
    assertPropExists(rev, "/foo", "p3");
    assertPropExists(rev, "/foo", "p4");
}
```

**Example (incorrect — misses collision cleanup check):**
```java
@Test
public void resetMultipleCommits() {
    addNodes(null, "/foo");
    String b0 = mk.branch(null);
    String b1 = mk.commit("", "^\"/foo/p1\":1", b0, null);
    String b2 = mk.commit("", "^\"/foo/p2\":1", b1, null);
    String b3 = mk.commit("", "^\"/foo/p3\":1", b2, null);
    mk.commit("", "^\"/foo/p2\":1^\"/foo/p3\":1", null, null);
    
    try {
        mk.merge(b3, null);
        fail("expected");
    } catch (DocumentStoreException expected) {}
    
    String b4 = mk.reset(b3, b1);
    String b5 = mk.commit("", "^\"/foo/p4\":1", b4, null);
    String rev = mk.merge(b5, null);
    // BUG: No assertion that collision markers were cleaned up!
    // The bug was that collisions.size() remained 1 instead of 0
    assertPropExists(rev, "/foo", "p1");
}
```