---
name: range-includes-cross-cluster-revision
description: WHEN testing Range.includes(Revision) methods that compare revisions,
  THEN verify the method correctly handles revisions from different cluster IDs without
  throwing exceptions. This skill applies when a method delegates to compareRevisionTime
  which throws IllegalArgumentException for mismatched cluster IDs.
code_tags:
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# range-includes-cross-cluster-revision

## Instructions

# Range.includes() Must Handle Different Cluster IDs Without Exception

## Instructions

- WHEN the TG encounters a `Range.includes(Revision r)` method that delegates to `Revision.compareRevisionTime(Revision other)` — which throws `IllegalArgumentException("Trying to compare revisions of different cluster ids: ...")` when `clusterId` values differ
- THEN the TG should write a test that creates two `Revision` objects with **different cluster IDs** (e.g., `Revision(0x200, 0, 1)` and `Revision(0x200, 0, 2)`) where one revision lies within the range's time bounds but has a different cluster ID, and verify the method returns `false` without throwing an exception
- Include concrete examples: use `new Revision(long timestamp, int counter, int clusterId)` with e.g. a Range(high=Revision(0x300, 0, 1), low=Revision(0x100, 0, 1), height=0) and test includes(Revision(0x200, 0, 2)) — this should return `false`, not throw an exception
- Common pitfall: testing only with matching cluster IDs, missing the cross-cluster case where `includes()` could crash
- Common pitfall: assuming `includes()` can just call `high.compareRevisionTime(r)` without guarding against cluster ID mismatch — the method must first check `high.getClusterId() == r.getClusterId()` before calling `compareRevisionTime()`

### Example (correct)
```java
@Test
public void includesDifferentClusterId() {
    Revision low = new Revision(0x100, 0, 1);
    Revision high = new Revision(0x300, 0, 1);
    Revision other = new Revision(0x200, 0, 2); // different clusterId
    Range range = new Range(high, low, 0);
    // Must NOT throw IllegalArgumentException
    assertFalse(range.includes(other));
}
```

### Example (incorrect — a test that would fail or miss the bug)
```java
@Test
public void includesOnlySameCluster() {
    Revision low = new Revision(0x100, 0, 1);
    Revision high = new Revision(0x300, 0, 1);
    Revision r = new Revision(0x200, 0, 1);
    Range range = new Range(high, low, 0);
    assertTrue(range.includes(r));
    // BUG: no test for cross-cluster revisions
    // The buggy code would throw:
    // IllegalArgumentException("Trying to compare revisions of different cluster ids")
}
```