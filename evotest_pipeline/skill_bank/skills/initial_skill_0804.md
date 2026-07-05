---
name: commit-root-purge-causes-merge-failure
description: When purging all but the most recent commit root in a document node store,
  the test must verify that subsequent merges fail with a CommitFailedException. This
  skill applies to tests that manipulate internal document store state (removing/reverting
  commit root entries) and then attempt a merge operation.
code_tags:
- STRING_MANIPULATION
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# commit-root-purge-causes-merge-failure

## Instructions

# Commit Root Purge Causes Merge Failure

## Instructions

- WHEN the TG encounters a test that removes or reverts commit root entries (e.g., via `DocumentNodeStore.revert()`, `remove()` calls on `commit-root` documents, or direct manipulation of `_commitRoot`, `_revertRoot`, `_revert` revision properties on node documents) and then performs a merge operation on the `DocumentNodeStore`
- THEN the test MUST use `assertThrows(CommitFailedException.class, ...)` on the merge operation, as purging all but the most recent commit root creates an inconsistent internal state that causes the next merge to fail with a `CommitFailedException`
- The test should also verify that the exception message contains relevant context (e.g., it must be a `CommitFailedException`, not a generic runtime exception). However, avoid asserting on exact message text as it may vary across versions.
- Common pitfalls to avoid:
  - Assuming merge will succeed after removing commit root revisions — it MUST fail with CommitFailedException
  - Using `try-catch` with `fail("merge must fail")` — instead use the cleaner `assertThrows` pattern
  - Forgetting to wrap operations in a test transaction context (e.g., using `getDocumentNodeStore().setReadOnly(false)` or calling `getDocumentNodeStore().revert(revision)` within the same cluster node setup)

### Example (Correct pattern — writing a test that exercises commit root purge):

```java
@Test
public void purgeAllButMostRecentCommitRoot() throws Exception {
    // ... setup with background operations, split, purge ...

    // After purge, attempt a merge:
    Thread t = new Thread(() -> {
        try {
            getDocumentNodeStore().merge(
                    getDocumentNodeStore().newBuilder()
                            .addNode("test")
                            .build()
            );
            fail("merge must fail with CommitFailedException");
        } catch (CommitFailedException e) {
            // expected
        }
    });
    t.start();
    t.join();
}
```

### Example (Incorrect pattern — assuming merge succeeds):

```java
@Test
public void testCommitRootPurge() {
    // ... setup and purge ...
    
    // BAD: This will throw CommitFailedException but code assumes it succeeds
    getDocumentNodeStore().merge(
        getDocumentNodeStore().newBuilder()
            .addNode("test")
            .build()
    );
    // Test passes on some states but fails on the buggy version
}
```

### Key implementation notes:
- The merge must be done in a separate thread that can receive the `CommitFailedException` asynchronously
- The test should call `t.join()` to wait for the merge thread to complete
- Use `fail("merge must fail with CommitFailedException")` in the try block, catching `CommitFailedException` in the catch block
- The merge builder should produce a valid commit operation (e.g., adding a node) that would normally succeed on a healthy store