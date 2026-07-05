---
name: concurrent-add-node-detection
description: WHEN testing document store commits that track added nodes in a HashSet,
  THEN test concurrent addition of the same node path across two sessions to verify
  the commit correctly detects conflicts. This skill catches missing conflict detection
  where the second commit silently overwrites instead of throwing OakMerge0004.
code_tags:
- CONCURRENCY_CHECK
- NULL_CHECK
test_pattern: INTERACTION_TEST
---

# concurrent-add-node-detection

## Instructions

# Concurrent Add-Node Conflict Detection

## Instructions

WHEN the TG encounters code that tracks added nodes in a `HashSet<String> addedNodes` field within a `Commit` class (for a document store), THEN the TG should write a test that:

1. **Creates two separate commit sessions** — obtain two `Commit` instances backed by the same underlying `DocumentStore`.
2. **Add the same node path** (e.g., `/foo`) via `commit.addNode(path)` in both sessions, ensuring the path string is identical.
3. **Commit the first session successfully** — call `commit.commit()` on the first instance.
4. **Attempt to commit the second session** — call `commit.commit()` on the second instance.
5. **Verify the second commit fails** with an `OakMerge0004` exception whose message contains the conflicting node path (e.g., `"1:/foo was already added in revision"`).

### Key pitfalls to avoid:
- **Testing only the happy path** — the TG might test that one commit succeeds but forget to verify that a concurrent commit of the same path actually fails.
- **Using different node paths** — the TG might add `/foo` in the first session and `/bar` in the second, which would not trigger the conflict.
- **Forgetting to check the exception type** — the TG might only check `commit.commit()` throws *some* exception, but must verify it throws an `OakMerge0004` with the correct message substring.
- **Overlooking concurrent setup** — the TG might attempt to reuse the same `Commit` object for both additions; two *separate* `Commit` instances (from two sessions on the same `DocumentNodeStore`) must be used.
- **Not calling `commit()` explicitly** — the failure only occurs upon `commit()`, not upon `addNode()`. A test that only calls `addNode()` would pass erroneously.

### Concrete example of the test structure:

```java
// Correct approach:
// 1. Get two separate sessions from the same store
// 2. Each session adds "/foo"
// 3. Commit the first session (succeeds)
// 4. Commit the second session (throws OakMerge0004)
DocumentNodeStore store = ...;
NodeBuilder builder1 = store.getRoot().builder();
NodeBuilder builder2 = store.getRoot().builder();

// Inside a test method:
NodeBuilder b1 = store.getRoot().builder();
b1.child("foo");
store.merge(b1, ...);  // succeeds

NodeBuilder b2 = store.getRoot().builder();
b2.child("foo");
assertThrows(CommitFailedException.class, () -> {
    store.merge(b2, ...);  // should throw OakMerge0004
});
```

```java
// INCORRECT approach:
NodeBuilder b = store.getRoot().builder();
b.child("foo");
store.merge(b, ...);  // only tests one session, misses the conflict

// Also INCORRECT:
NodeBuilder b1 = store.getRoot().builder();
b1.child("foo");
store.merge(b1, ...);
// No second session — no concurrent conflict tested
```