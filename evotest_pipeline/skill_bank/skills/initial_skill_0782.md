---
name: comparator-transitivity-violation
description: Detects when a Comparator does not obey the transitivity contract (if
  a>b and b>c then a>c must hold). This skill applies when comparing objects with
  compound fields where equality on one field falls through to subsequent fields,
  but the first field comparison may be inconsistent with the overall ordering.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
test_pattern: STATE_TEST
---

# comparator-transitivity-violation

## Instructions

# Comparator Transitivity Violation

## Instructions

- WHEN the TG encounters a `Comparator` implementation (or a `compareTo` method) that compares objects by multiple fields in sequence (e.g., compare timestamp, then counter, then clusterId), and the fields being compared include values that are compared using integer relational operators (`<`, `>`) rather than subtraction
- THEN the TG should test that the comparator obeys the general contract of `Comparator.compare()` (or `Comparable.compareTo()`) — specifically **transitivity**: if `compare(a, b) > 0` and `compare(b, c) > 0`, then `compare(a, c) > 0` must also hold. The TG should construct three objects where pairwise comparisons yield transitive results and verify using `assertTrue("Expected positive but got negative", result > 0)` or `assertEquals(expected, result)`.
- Include concrete values/types/examples: For `Revision.compareTo()`, the comparison order is (1) timestamp as `long`, (2) counter as `int`, (3) clusterId as `int`, and then (4) branch flag as `boolean`. A violation occurs when two revisions that are equal on timestamp, counter, and clusterId but differ only on `branch` produce inconsistent ordering (e.g., r1 < r2 when compared both ways, or transitivity breaks across the branch field).
- The test should verify the comparator's behavior with a `SortedSet` or `TreeSet` containing the comparator — if the comparator violates transitivity, the set may behave incorrectly (e.g., include duplicate entries or miss entries). Verify by adding objects to the set and checking `set.size()`.
- Common pitfalls to avoid:
  1. Testing only with revisions from the same cluster ID (which bypasses the clusterId comparison path)
  2. Testing only pairwise comparisons without checking transitivity across three or more objects
  3. Not testing the `branch` field comparison — the bug occurs when `branch` comparison flips the sign returned by `compareRevisionTimeThenClusterId`, breaking transitivity with other revisions
  4. Assuming the comparator's logic is fine because simple pair comparisons pass
  5. Not using a `TreeSet` or `SortedSet` to detect transitivity violations at runtime

## Example

Correct test (catches the bug):

```java
// Create revisions where r1 < r2 < r3 should hold transitively
// r1 and r2 differ in branch, r2 and r3 differ in branch
Revision r1 = new Revision(10, 0, 0, true);  // branch=true
Revision r2 = new Revision(10, 0, 0, false); // branch=false (same timestamp, counter, clusterId)
Revision r3 = new Revision(20, 0, 0, true);  // later timestamp

// StableRevisionComparator delegates to Revision.compareTo
Comparator<Revision> cmp = StableRevisionComparator.INSTANCE;

// Check pairwise
int c1 = cmp.compare(r1, r2);
int c2 = cmp.compare(r2, r3);
int c3 = cmp.compare(r1, r3);

// If compareTo returns branch ? -1 : 1 for same-timestamp revisions,
// then r1 < r2 (c1 < 0), r2 < r3 (c2 < 0), but r1 > r3 (c3 > 0) — violation!
assertTrue("Comparator must be transitive", 
    !(c1 > 0 && c2 > 0 && c3 <= 0) && 
    !(c1 < 0 && c2 < 0 && c3 >= 0));

// Stronger: use a TreeSet to detect the violation
TreeSet<Revision> set = new TreeSet<Revision>(cmp);
set.add(r1);
set.add(r2);
set.add(r3);
assertEquals("TreeSet should contain all 3 elements", 3, set.size());
```

Incorrect test (misses the bug):

```java
// Only testing same-cluster revisions
Revision r1 = new Revision(10, 0, 0, false);
Revision r2 = new Revision(20, 0, 0, false);
assertTrue("r1 < r2", StableRevisionComparator.INSTANCE.compare(r1, r2) < 0);

// This passes fine but misses the transitivity bug with branch field
```