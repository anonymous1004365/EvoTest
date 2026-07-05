---
name: modified-timestamp-reset-testing
description: When dealing with timestamp fields that are stored with coarse resolution
  (e.g., 5-second buckets) and may be reset/purged during operations like diff computation,
  test that timestamps are correctly preserved or recomputed rather than lost or set
  to zero.
code_tags:
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# modified-timestamp-reset-testing

## Instructions

# Modified Timestamp Reset Testing

## Instructions

WHEN the TG encounters code that maintains a `_modified` timestamp field (e.g., `MODIFIED_IN_SECS`) with a coarse resolution (e.g., `MODIFIED_IN_SECS_RESOLUTION = 5` seconds) on a document, and there is logic that can reset, purge, or recompute this timestamp during operations like diff computation, background operations, or cache invalidation:

- THEN the TG should verify that the timestamp value is correctly preserved or recomputed to a non-zero, meaningful value (not reset to 0 or lost)
- Use a `Clock.Virtual` to control time precisely so that the test can deterministically reproduce the boundary condition where the timestamp resolution causes a problem
- Wait at least `MODIFIED_IN_SECS_RESOLUTION + 1` seconds (using `SECONDS.toMillis(MODIFIED_IN_SECS_RESOLUTION + 1)`) between commits to ensure commits fall into different resolution buckets
- Use `Revision.setClock(clock)` to set a virtual clock on the revision system
- Make assertions on the actual stored `_modified` value (e.g., via `NodeDocument.MODIFIED_IN_SECS`) to confirm it reflects the correct time bucket, not 0 or an incorrect value

Common pitfalls:
- Testing with only a single commit rather than two commits where the second commit triggers the reset logic
- Not advancing the virtual clock enough between commits (advancing by less than `MODIFIED_IN_SECS_RESOLUTION + 1` seconds may keep commits in the same bucket, masking the bug)
- Forgetting to call `Revision.setClock(clock)` which is needed for the virtual clock to take effect
- Assuming timestamps are monotonically increasing without verifying the actual stored value after operations like diff computation or cache invalidation
- Using `System.currentTimeMillis()` instead of a controlled virtual clock, which makes the test non-deterministic

### Correct approach (concrete example from this codebase):

```java
// Setup virtual clock for deterministic time control
Clock clock = new Clock.Virtual();
clock.waitUntil(System.currentTimeMillis());
Revision.setClock(clock);

DocumentNodeStore store = new DocumentMK.Builder()
    .setDocumentStore(docStore)
    .setClusterId(1)
    .setAsyncDelay(0)
    .clock(clock)
    .getNodeStore();

// Make first commit
NodeBuilder builder = store.getRoot().builder();
builder.child("node");
store.merge(builder, EmptyHook.INSTANCE, CommitInfo.EMPTY);

// Wait past resolution boundary (>5 seconds in this implementation)
clock.waitUntil(System.currentTimeMillis() + 
    SECONDS.toMillis(MODIFIED_IN_SECS_RESOLUTION + 1));

// Make second commit that may trigger the reset
builder = store.getRoot().builder();
builder.child("node").child("child");
store.merge(builder, EmptyHook.INSTANCE, CommitInfo.EMPTY);

// Now trigger the operation that may reset the timestamp
store.runBackgroundOperations();
String diff = store.diffChildren(root2, root1);

// Verify the _modified timestamp is correct (not 0 or lost)
// Assert that the node appears in the diff as changed
assertEquals("^\"node\":{}", diff.trim());
```

### Incorrect approach (won't catch this bug):

```java
// Using real time - non-deterministic
DocumentNodeStore store = new DocumentMK.Builder()
    .setAsyncDelay(0)
    .getNodeStore();

// Only one commit - doesn't trigger the reset path
NodeBuilder builder = store.getRoot().builder();
builder.child("node");
store.merge(builder, EmptyHook.INSTANCE, CommitInfo.EMPTY);

// No time advancement between commits
builder = store.getRoot().builder();
builder.child("node").child("child");
store.merge(builder, EmptyHook.INSTANCE, CommitInfo.EMPTY);

// Doesn't verify timestamp value, only checks if node exists
assertTrue(store.getRoot().hasChildNode("node"));
```