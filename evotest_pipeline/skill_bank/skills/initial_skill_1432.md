---
name: comparable-revision-timestamp-ordering
description: When testing a Comparable implementation where ordering depends on two
  fields (timestamp first, then clusterId), the TG must verify that objects with equal
  timestamps but different clusterIds are correctly ordered by the secondary field.
  Without testing this, subtle comparison inversions can go undetected.
code_tags:
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# comparable-revision-timestamp-ordering

## Instructions

# Comparable Revision Timestamp and ClusterId Ordering

## Instructions

- WHEN the TG encounters a `Comparable` or `Comparator` class that compares two fields with a precedence order (e.g., timestamp first, then cluster ID as tiebreaker)
- THEN the TG must write a test that creates **multiple pairs** of objects where:
  1. Two objects have the **same primary field value** (same timestamp) but **different secondary field values** (different cluster IDs)
  2. The test verifies the ordering of the secondary field is respected (e.g., lower clusterId should come before higher clusterId when timestamps are equal)
  3. The test checks `a.compareTo(b)` returns a negative value, `b.compareTo(a)` returns a positive value, and both are consistent with `a.equals(b) == false`
- For the `Revision` class in `org.apache.jackrabbit.oak.plugins.document`, when timestamps are equal (both `getTimestamp()` returning the same value), the `compareRevisionTimeThenClusterId` method should order by `getClusterId()` only. The TG must test at least two `Revision` objects with the same timestamp but different cluster IDs.
- Common pitfalls to avoid:
  - Testing only objects with different timestamps, which misses the tiebreaker bug
  - Failing to test the transitivity: if a < b and b < c then a < c
  - Forgetting to test both directions (a vs b AND b vs a)
  - Assuming `compareTo` returns exactly -1 or 1 rather than just negative/positive
  - Not testing the case where both fields are equal (return value must be 0)

### Correct Example (detects the bug)
```java
// Revision1: same timestamp, lower clusterId
Revision rev1 = Revision.newRevision(1, 1, 0);  // timestamp=1, clusterId=1
// Revision2: same timestamp, higher clusterId
Revision rev2 = Revision.newRevision(1, 2, 0);  // timestamp=1, clusterId=2

assertTrue("rev1 should be less than rev2 (same timestamp, lower clusterId)", 
           rev1.compareRevisionTimeThenClusterId(rev2) < 0);
assertTrue("rev2 should be greater than rev1 (same timestamp, higher clusterId)", 
           rev2.compareRevisionTimeThenClusterId(rev1) > 0);
```

### Incorrect Example (misses the bug)
```java
// Only testing with different timestamps — entirely misses the tiebreaker logic
Revision rev1 = Revision.newRevision(100, 1, 0);
Revision rev2 = Revision.newRevision(200, 2, 0);
assertTrue(rev1.compareRevisionTimeThenClusterId(rev2) < 0); // Passes even if tiebreaker is broken
```