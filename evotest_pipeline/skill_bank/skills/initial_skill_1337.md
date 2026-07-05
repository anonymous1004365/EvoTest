---
name: unique-index-insert-duplication-detection
description: When testing index store strategies that insert entries with a "match"
  property under key nodes, the TG should verify that duplicate inserts for the same
  key produce exactly one leaf entry rather than multiple. This skill catches bugs
  where the count of unique entries is inflated due to overlapping path structures.
code_tags:
- STATE_MUTATION
- BOUNDARY_CHECK
- CONCURRENCY
test_pattern: STATE_TEST
---

# unique-index-insert-duplication-detection

## Instructions

# Unique Index Insert Duplication Detection

## Instructions

- WHEN the TG encounters an `IndexStoreStrategy` (or similar) that uses a shared key node via `fetchKeyNode()` combined with `builder.child(name)` to create path-like entries under that key, AND the `update()` method is called multiple times with different paths but the same key (e.g., `"a"` and `"b"` both under key `"key"`)
- THEN the TG MUST write a test that:
  1. Creates an `IndexStoreStrategy` instance (e.g., `new ContentMirrorStoreStrategy()`)
  2. Creates an empty `NodeState` (e.g., `EMPTY_NODE`) and obtains a `NodeBuilder` from it
  3. Wraps the builder in a `Supplier<NodeBuilder>` (e.g., using `Suppliers.memoize(() -> builder.child(INDEX_CONTENT_NODE_NAME))` to simulate the index meta node pattern)
  4. Calls `store.update(index, "pathA", null, null, EMPTY, KEYSET)` then `store.update(index, "pathB", null, null, EMPTY, KEYSET)` with the same key set and different paths
  5. Calls `store.count(root, indexMeta.getNodeState(), Collections.singleton("key"), maxTraversal)` (e.g., `maxTraversal = 2`)
  6. Asserts that the count is **greater than 1** — because each unique path should be counted separately, not merged

- Common mistakes to avoid:
  - Testing with only a single insert/update — the bug only manifests with **two or more** inserts using the same key but different paths
  - Using `builder.child("key")` directly instead of wrapping via `memoize(() -> builder.child(...))` — the test must replicate the real `update()` supplier pattern where `index.get()` is called repeatedly
  - Asserting an exact count (e.g., `assertEquals(2, count)`) — the buggy version may return 1, so assert `count > 1` to detect the lack of uniqueness
  - Using the same path for both inserts — the paths must be **different** (e.g., `"a"` and `"b"`) to test uniqueness
  - Forgetting that `count()` requires `Collections.singleton("key")` as the `values` parameter (not `null`) to count entries for a specific key

- **Correct example (what the test should do):**
```java
@Test
public void testUnique() {
    IndexStoreStrategy store = new ContentMirrorStoreStrategy();
    NodeState root = EMPTY_NODE;
    NodeBuilder indexMeta = root.builder();
    Supplier<NodeBuilder> index = memoize(() -> indexMeta.child(INDEX_CONTENT_NODE_NAME));
    store.update(index, "a", null, null, EMPTY, newHashSet("key"));
    store.update(index, "b", null, null, EMPTY, newHashSet("key"));
    assertTrue(
        "ContentMirrorStoreStrategy should guarantee uniqueness on insert",
        store.count(root, indexMeta.getNodeState(), Collections.singleton("key"), 2) > 1);
}
```

- **Incorrect example (would NOT catch the bug):**
```java
@Test
public void testUniqueIncorrect() {
    IndexStoreStrategy store = new ContentMirrorStoreStrategy();
    NodeState root = EMPTY_NODE;
    NodeBuilder builder = root.builder();
    Supplier<NodeBuilder> index = () -> builder;  // wrong supplier pattern
    store.update(index, "a", null, null, EMPTY, newHashSet("key"));
    store.update(index, "b", null, null, EMPTY, newHashSet("key"));
    assertEquals(2, store.count(root, builder, Collections.singleton("key"), 2));  // wrong NodeState and exact assertion
}
```