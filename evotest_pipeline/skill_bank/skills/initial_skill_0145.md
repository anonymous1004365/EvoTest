---
name: segment-nodestore-infinite-checkpoint-lifetime
description: When creating checkpoints in a SegmentNodeStore, the checkpoint method
  accepts a lifetime parameter in milliseconds. Without validation, passing Long.MAX_VALUE
  can cause an overflow when converting to the internal scheduler representation,
  leading to unexpected behavior. Use this skill to test boundary values for checkpoint
  lifetime and verify that the system handles them gracefully.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# segment-nodestore-infinite-checkpoint-lifetime

## Instructions

# SegmentNodeStore Checkpoint Lifetime Boundary Validation

## Instructions

- WHEN the TG encounters a `NodeStore.checkpoint(long lifetime, Map<String, String> properties)` or `NodeStore.checkpoint(long lifetime)` method that passes `lifetime` to a scheduler or internal queue, and the method involves converting the time unit (e.g., from milliseconds to seconds or vice versa)
- THEN the TG should test with the boundary value `Long.MAX_VALUE` as the `lifetime` parameter and verify that:
  1. Calling `store.checkpoint(Long.MAX_VALUE)` does not throw an exception on the buggy version (if the bug is silent overflow), or
  2. Calling `store.checkpoint(Long.MAX_VALUE)` with a subsequent `store.release(checkpoint)` does not cause the checkpoint limit to be exceeded (if the bug involves the `maxCheckpoints` count being incorrectly decremented)
  3. The test should create a checkpoint with `Long.MAX_VALUE`, release it, then create multiple other checkpoints and verify that creation succeeds and the expected number of checkpoints is observed

- WHEN the TG sees a `NodeStore.checkpoint` implementation that stores checkpoints in a collection with bounded size (e.g., a max checkpoints limit)
- THEN the TG should test that releasing a checkpoint correctly decrements the internal counter, especially when checkpoints with extreme lifetime values (like `Long.MAX_VALUE`) are involved

- **Common pitfalls**:
  - Testing only valid positive lifetime values (e.g., 1000, 3600000) without testing extreme boundaries like `Long.MAX_VALUE`
  - Assuming that checkpoint lifetime overflow (e.g., `Long.MAX_VALUE / 1000` overflowing `long` when converting to seconds) is handled
  - Assuming `release()` on a checkpoint always properly decrements the checkpoint count without testing the edge case of checkpoints created with extreme lifetimes
  - Not using `@After` cleanup to release checkpoints after the test

- **Example (correct test pattern)**:
```java
@Test
public void testCheckpointMax() throws CommitFailedException, IOException {
    String cp0 = store.checkpoint(Long.MAX_VALUE);
    store.release(cp0);
    String cp1 = store.checkpoint(10000);
    String cp2 = store.checkpoint(10000);
    String cp3 = store.checkpoint(10000);
    String cp4 = store.checkpoint(10000);
    // Verify all checkpoints were created successfully
    assertNotNull(cp1);
    assertNotNull(cp2);
    assertNotNull(cp3);
    assertNotNull(cp4);
}
```

- **Example (incorrect test pattern — only tests normal values)**:
```java
@Test
public void testCheckpointNormal() {
    String cp = store.checkpoint(60000);
    assertNotNull(cp);
    store.release(cp);
    // Missed the boundary case with Long.MAX_VALUE
}
```