---
name: timestamp-difference-overflow-same-cluster
description: When testing timestamp difference or time arithmetic between two items
  from the same cluster node, test with reversed argument order to detect integer
  overflow due to unsigned-to-signed long subtraction. The bug manifests when the
  result is expected to be positive but instead returns a wrong small number.
code_tags:
- ARITHMETIC_OVERFLOW
- STATE_MUTATION
- ARGUMENT_VALIDATION
test_pattern: PARAMETRIC_TEST
---

# timestamp-difference-overflow-same-cluster

## Instructions

# Timestamp Difference Overflow for Same-Cluster Revisions

## Instructions

- WHEN the TG encounters a method that computes a timestamp difference between two objects using plain `long` subtraction (e.g., `r1.getTimestamp() - r2.getTimestamp()`), and the timestamps are non-negative unsigned-like longs stored as signed Java longs
- THEN the TG should write a test using two revisions that share the **same cluster ID** but whose timestamp difference crosses the `Long.MAX_VALUE` boundary, verifying that the difference is computed correctly as expected (a large positive long, not a small or negative number due to overflow)
  - Specifically, create `Revision` objects directly via constructor `new Revision(timestamp, counter, clusterId)` rather than via `newRevision()`, so that timestamps can be set to arbitrary large values
  - Use `Long.MAX_VALUE` as one timestamp and `0` as the other, with the same `counter` and `clusterId` values to isolate the timestamp arithmetic
  - Verify that `Revision.getTimestampDifference(r1, r2)` returns the correct arithmetic difference: `r1.getTimestamp() - r2.getTimestamp()` should equal `r1.timestamp - r2.timestamp` as a `long`, even when the subtraction would overflow in unsigned arithmetic
  - NOTE: The bug is that `getTimestampDifference` uses bare `long` subtraction which is correct for signed arithmetic but callers may interpret the result incorrectly as if timestamps are unsigned values. The test should assert the mathematically expected result.
- Common pitfalls to avoid:
  - Testing only timestamps in the normal millisecond range (e.g., current system time) — this won't trigger the bug
  - Using `newRevision()` instead of the constructor — `newRevision()` generates timestamps near the current time, which are far from overflow
  - Testing with different cluster IDs — the bug in question relates to same-cluster-ID scenarios where the timestamp is the primary differentiator
  - Using `assertEquals` with a hardcoded expected value — the expected value should be computed as `r1.getTimestamp() - r2.getTimestamp()` or the known difference

### Correct example (catches the bug):
```java
@Test
public void getMinimumTimestampSingleClusterId() {
    // Two revisions with same clusterId (0) where timestamp difference overflows
    Revision r1 = new Revision(Long.MAX_VALUE, 0, 0);
    Revision r2 = new Revision(0, 0, 0);
    // Both revisions have same clusterId, so getTimestampDifference should work
    long diff = Revision.getTimestampDifference(r1, r2);
    // The difference is Long.MAX_VALUE - 0 = Long.MAX_VALUE
    assertEquals(Long.MAX_VALUE, diff);
    
    // Reverse case: smaller timestamp minus larger timestamp
    long diff2 = Revision.getTimestampDifference(r2, r1);
    assertEquals(-Long.MAX_VALUE, diff2);
}
```

### Incorrect example (misses the bug):
```java
@Test
public void difference() throws InterruptedException {
    // Only tests timestamps near current time — never hits overflow
    long t0 = Revision.getCurrentTimestamp();
    Revision r0 = Revision.newRevision(0);
    Revision r1 = Revision.newRevision(0);
    long t1 = Revision.getCurrentTimestamp();
    assertTrue(Revision.getTimestampDifference(r1, r0) <= (t1 - t0));
}
```