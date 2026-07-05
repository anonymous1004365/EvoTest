---
name: checkpoint-exactly-on-same-revision-overwrite
description: When checkpoints are created on same revision using createOrUpdate (which
  overwrites map entries), the second checkpoint overwrites the first because they
  share the same revision key in the PROP_CHECKPOINT map. This skill teaches how to
  test for this collision by ensuring checkpoints use unique revisions.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# checkpoint-exactly-on-same-revision-overwrite

## Instructions

# Checkpoint Collision on Same Revision

## Instructions

### WHEN the TG encounters code that creates checkpoints by storing entries in a map (e.g., `op.setMapEntry(PROP_CHECKPOINT, r, ...)`) using `createOrUpdate` on a collection, where the map key is a `Revision` object:

- **THEN** the TG should test what happens when two checkpoints are created at the exact same revision (i.e., when the head revision has NOT changed between checkpoint calls).

- **THEN** the test should:
  1. Create a first checkpoint with a long expiry time (e.g., `TimeUnit.HOURS.toMillis(3)`).
  2. Capture the checkpoint revision string (`c2`).
  3. WITHOUT making any commits (to keep head revision unchanged), create a second checkpoint with a shorter expiry time (e.g., `TimeUnit.HOURS.toMillis(1)`).
  4. Capture the second checkpoint revision string (`c1`).
  5. Advance the clock past the shorter expiry time so it expires.
  6. Call `store.getCheckpoints().getOldestRevisionToKeep()` which triggers cleanup of expired checkpoints.
  7. Assert that the older (longer-lived) checkpoint is STILL retrievable (`assertNotNull(store.retrieve(c2))`).
  8. Assert that the expired checkpoint is gone (`assertNull(store.retrieve(c1))`).

- **THEN** the TG should verify the concrete failure: on the buggy version, when both checkpoints share the same revision key in the data map, the second `createOrUpdate` overwrites the first. After cleanup, the checkpoint for `c2` is lost (`expected:<r...> but was:<null>`).

### Common pitfalls to avoid:
- ❌ **Pitfall**: Creating checkpoints on different revisions (by inserting a commit between them). This avoids the collision entirely, making the test pass even on buggy code.
  - **Correct**: Do NOT modify the head revision between the two checkpoint calls, so they naturally get the same revision.
- ❌ **Pitfall**: Only testing with a single checkpoint per revision.
- ❌ **Pitfall**: Assuming `createOrUpdate` with `setMapEntry` will merge entries — it OVERWRITES if the key already exists.
- ❌ **Pitfall**: Forgetting to use `Clock.Virtual` to precisely control time and trigger checkpoint expiry.

### Example (correct test pattern):

```java
@Test
public void multipleCheckpointOnSameRevision() throws Exception{
    long e1 = TimeUnit.HOURS.toMillis(1);  // shorter expiry
    long e2 = TimeUnit.HOURS.toMillis(3);  // longer expiry

    // Create checkpoint with HIGHER expiry first
    String c2 = store.checkpoint(e2);

    // NO commit between checkpoints — same head revision
    String c1 = store.checkpoint(e1);  // this can overwrite c2's entry!

    // Advance clock past the shorter expiry
    clock.waitUntil(clock.getTime() + e1 + 1);

    // The longer-lived checkpoint must survive cleanup
    assertEquals(1, store.getCheckpoints().size());
    assertNull(store.retrieve(c1));
    assertNotNull("c2 must still be retrievable", store.retrieve(c2));
}
```

### Example (incorrect test that misses the bug):

```java
@Test
public void testCheckpointsDifferentRevisions() throws Exception{
    String c2 = store.checkpoint(TimeUnit.HOURS.toMillis(3));

    // This commit changes head revision, so second checkpoint
    // gets a different revision key — no collision occurs
    NodeBuilder b = store.getRoot().builder();
    b.child("x");
    store.merge(b, EmptyHook.INSTANCE, CommitInfo.EMPTY);

    String c1 = store.checkpoint(TimeUnit.HOURS.toMillis(1));
    // Test passes even on buggy code because revisions differ
}
```