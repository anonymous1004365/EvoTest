---
name: checkpoint-operator-id-validation
description: When building checkpoint statistics trackers that accept operator IDs
  or checkpoint IDs from external callers, the TG should test that illegal/negative
  operator IDs trigger IllegalArgumentException. This skill helps validate that PendingCheckpointStats
  properly rejects invalid subtask operator IDs.
code_tags:
- VALIDATION
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# checkpoint-operator-id-validation

## Instructions

# Checkpoint Operator ID Validation

## Instructions

- WHEN the TG encounters a `CheckpointStatsTracker` (or similar stats tracker) that accepts `reportPendingCheckpoint()` returning a `PendingCheckpointStats` object, and that object has a `reportSubtaskStats(JobVertexID, SubtaskStateStats)` method
- THEN the TG should verify that attempting to report subtask stats with an invalid/negative operator ID (e.g., `-1`) on the `PendingCheckpointStats` properly throws an `IllegalArgumentException`
- Include at least one test method annotated with `@Test(expected = IllegalArgumentException.class)` that:
  1. Creates a mock `ExecutionJobVertex` with a valid `JobVertexID` and `parallelism` (e.g., 3)
  2. Creates a `CheckpointStatsTracker` with `numRememberedCheckpoints=0`, the mock job vertex, a mock `CheckpointCoordinatorConfiguration`, and an `UnregisteredMetricsGroup`
  3. Calls `tracker.reportPendingCheckpoint(0L, 1L, CheckpointProperties.forStandardCheckpoint())` to get a `PendingCheckpointStats`
  4. Creates a `SubtaskStateStats` using `createSubtaskStats(int index)` or `new SubtaskStateStats(int index, ...)` — do NOT mock `SubtaskStateStats`
  5. Calls `pending.reportSubtaskStats(jobVertex.getJobVertexId(), subtaskStateStats)` where the subtask index is negative (e.g., `-1`)
- The test should expect `IllegalArgumentException` to be thrown when reporting a subtask with a negative operator ID
- Common pitfalls to avoid:
  - Testing only with valid operator IDs (positive integers) — the bug is triggered by negative/illegal IDs
  - Mocking `SubtaskStateStats` instead of using a real instance — the validation is inside the `PendingCheckpointStats.reportSubtaskStats()` method, which checks the subtask index from the `SubtaskStateStats`
  - Forgetting to call `reportPendingCheckpoint()` first — the `PendingCheckpointStats` needs to be obtained from the tracker before you can report subtask stats on it
  - Testing at the wrong level — the TG should test the `PendingCheckpointStats.reportSubtaskStats()` method's validation, not just the tracker's constructor

**Correct example:**
```java
@Test(expected = IllegalArgumentException.class)
public void testIllegalOperatorId() throws Exception {
    ExecutionJobVertex jobVertex = mock(ExecutionJobVertex.class);
    when(jobVertex.getJobVertexId()).thenReturn(new JobVertexID());
    when(jobVertex.getParallelism()).thenReturn(3);

    CheckpointStatsTracker tracker = new CheckpointStatsTracker(
        0,
        Collections.singletonList(jobVertex),
        mock(CheckpointCoordinatorConfiguration.class),
        new UnregisteredMetricsGroup());

    PendingCheckpointStats pending = tracker.reportPendingCheckpoint(
        0L,
        1L,
        CheckpointProperties.forStandardCheckpoint());

    pending.reportSubtaskStats(jobVertex.getJobVertexId(), createSubtaskStats(-1));
}

private SubtaskStateStats createSubtaskStats(int index) {
    return new SubtaskStateStats(index, ...);
}
```

**Incorrect example (will NOT catch the bug):**
```java
@Test
public void testValidCheckpointTracking() throws Exception {
    // This test only uses valid indices >= 0
    ExecutionJobVertex jobVertex = mock(ExecutionJobVertex.class);
    when(jobVertex.getJobVertexId()).thenReturn(new JobVertexID());
    when(jobVertex.getParallelism()).thenReturn(3);
    CheckpointStatsTracker tracker = new CheckpointStatsTracker(10, ...);
    PendingCheckpointStats pending = tracker.reportPendingCheckpoint(0, 1, CheckpointProperties.forStandardCheckpoint());
    pending.reportSubtaskStats(jobVertex.getJobVertexId(), createSubtaskStats(0));
    pending.reportCompletedCheckpoint(null);
    // No assertion for illegal values - this test is necessary but insufficient
}
```