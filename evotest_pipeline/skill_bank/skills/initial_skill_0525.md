---
name: aborted-repair-duration-null-handling
description: When computing duration for aborted/cancelled/failed repair runs, the
  test generator should verify that null or missing end_time fields don't cause silent
  issues with duration calculations. This skill ensures proper null-safety testing
  for temporal fields in repair status views.
code_tags:
- VALIDATION
- STATE_MUTATION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# aborted-repair-duration-null-handling

## Instructions

# Handling Null End Times in Repair Duration Calculations

## Instructions

- WHEN the TG encounters code that computes a duration between a `startTime` and `endTime` (or a `RepairSegment`'s `endTime`) for a repair run, especially when the repair run has an aborted, cancelled, or failed state
- THEN the TG MUST write a test that creates a `RepairRunStatus` or equivalent view object with a null `endTime` in the relevant `RepairSegment` (or repair run) and verifies that calling the `getDuration()` or equivalent method does NOT throw a `NullPointerException` — it should gracefully handle the null (e.g., return `Duration.ZERO` or `null`).
- The test should specifically:
  1. Create a `RepairSegment` (or equivalent) with `state` set to `RUNNING`, `DONE`, `ABORTED`, `FAILED`, or `ERROR` — but with `endTime` set to `null`.
  2. Build a `RepairRunStatus` that includes this segment.
  3. Call the method that computes duration (e.g., `segment.getDuration()`, `repairRunStatus.getDuration()`, etc.).
  4. Assert that the call completes without exception (and returns a sensible default value like `Duration.ZERO`).

- **Common pitfall**: Only testing with non-null endTime values will miss the bug. Many codebases assume `endTime` is always non-null for completed/aborted segments, but in practice it can be `null` (e.g., a segment was aborted before the end time was recorded).

- **Correct example**:
```java
@Test
public void testAbortedRepairDuration() {
    RepairSegment segment = RepairSegment.builder()
        .withStartTime(Instant.now().minus(10, ChronoUnit.MINUTES))
        .withEndTime(null)    // <-- null endTime for aborted segment
        .withState(RepairSegment.State.ABORTED)
        .build();
    
    // The method should not throw NPE
    Duration duration = segment.getDuration();
    assertNotNull(duration);  // Should return a valid Duration, e.g., Duration.ZERO
}
```

- **Incorrect example (will miss the bug)**:
```java
@Test
public void testAbortedRepairDuration() {
    RepairSegment segment = RepairSegment.builder()
        .withStartTime(Instant.now().minus(10, ChronoUnit.MINUTES))
        .withEndTime(Instant.now())  // <-- never tests with null!
        .withState(RepairSegment.State.ABORTED)
        .build();
    
    Duration duration = segment.getDuration();
    assertNotNull(duration);
}
```

- **Additional variants to consider**: Test with `state = RUNNING` (no endTime yet), `state = FAILED`, and `state = ERROR` — all can have null endTime in real scenarios.

- The failure expected on the **buggy** version is a `NullPointerException` at the point where `endTime` is implicitly dereferenced (e.g., `Duration.between(startTime, endTime)` where `endTime` is null). On the **fixed** version, the code should handle null with a conditional check.