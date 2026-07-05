---
name: checkpoint-stats-state-size-overflow
description: When aggregating pending checkpoint stats into completed checkpoint stats,
  test that stateSize values are computed without overflow. Apply when a pending stats
  object (with long fields) is converted to a completed stats object (with int fields),
  verifying that large long values do not silently overflow.
code_tags:
- BOUNDARY_CHECK
- RESOURCE_MANAGEMENT
- STATE_MUTATION
test_pattern: STATE_TEST
---

# checkpoint-stats-state-size-overflow

## Instructions

# Checkpoint Stats State Size Overflow Detection

## Instructions

### WHEN the TG encounters code that aggregates `PendingCheckpointStats` into `CompletedCheckpointStats`, specifically where a `long stateSize` field from the pending stats is converted or assigned to an `int stateSize` in the completed stats, and the aggregation involves summing multiple state sizes from subtasks.

### THEN the TG should write a test that:

1. **Create a `PendingCheckpointStats` with a very large `stateSize` value that exceeds `Integer.MAX_VALUE`** (e.g., `4294967296L` which is `Integer.MAX_VALUE * 2`, or `-4982714695508294559L` as seen in the actual bug).

2. **Trigger the completion/reordering path** that converts the pending stats into completed stats:
   - Call the method that reorders completed checkpoints (e.g., `reportCompletedCheckpoint` or similar stats tracker method).
   - Ensure the pending stats tracker aggregates the state size from the pending stats into the completed stats.

3. **Verify that the `stateSize` in the resulting `CompletedCheckpointStats` matches the original value exactly** (no overflow):
   - Assert that `completedStats.getStateSize()` equals the original `long` value from the pending stats.
   - Do NOT assert using casts like `(int) longValue` which would mask the overflow.

4. **Test with both normal (small) and overflow-inducing (large) state size values:**
   - A small value (e.g., `100L`) to verify normal operation.
   - A large value exceeding `Integer.MAX_VALUE` (e.g., `4294967296L` or `-4982714695508294559L`) to detect overflow.

### Common pitfalls to avoid:

- ❌ **Only testing with small state sizes** — This misses the overflow bug entirely. The bug only manifests with large long values.
- ❌ **Casting the expected value to `int` in the assertion** — e.g., `assertEquals((int)largeValue, result)` would pass even with the bug.
- ❌ **Assuming `stateSize` is stored as `long` everywhere** — Verify the actual field types in `CompletedCheckpointStats`. If it stores `int`, overflow is possible.
- ❌ **Testing `PendingCheckpointStats` in isolation** — The overflow occurs during the aggregation/conversion step, not in the pending stats object itself.

### Example test pattern:

```java
// Correct approach:
PendingCheckpointStats pending = createPendingCheckpointStats();
// Set a large state size that would overflow if cast to int
long largeStateSize = 4294967296L; // > Integer.MAX_VALUE
pending.setStateSize(largeStateSize);

// Trigger the completion/reordering
CompletedCheckpointStats completed = tracker.completePendingCheckpoint(pending);

// Assert using long comparison, NOT cast to int
assertEquals(largeStateSize, completed.getStateSize()); // PASSES only if no overflow

// Incorrect approach that would miss the bug:
// assertEquals((int)largeStateSize, completed.getStateSize()); // Would pass even with overflow bug
```

### What to verify on the buggy version:

- On the buggy version, the test should **fail** with a mismatch, e.g.:  
  `expected:<CheckpointStats{...stateSize=4294967296}> but was:<CheckpointStats{...stateSize=1234567890}>`
- On the fixed version, the same test should **pass**.