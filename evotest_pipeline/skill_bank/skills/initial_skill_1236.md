---
name: comparator-total-order-violation
description: When testing protocols/decoders that sort or compare objects, verify
  that comparators respect the total order contract (reflexivity, symmetry, transitivity).
  This skill detects bugs where comparison logic has inconsistent results, e.g., reporting
  equals but non-zero hashCode or self-inequality.
code_tags:
- SORT_COMPARATOR_INTEGRITY
test_pattern: STATE_TEST
---

# comparator-total-order-violation

## Instructions

# Comparator Total Order Violation Detection

## Instructions

- WHEN the TG encounters a protocol decoder or handler class (like `V680ProtocolDecoder`) that sorts or compares custom objects (e.g., positions, events, messages) using a `Comparable` interface or `Comparator` implementation:
  - THEN it should write a test that checks the comparator's consistency properties:
    1. **Reflexivity**: `compare(a, a) == 0` for any non-null value `a`
    2. **Symmetry**: `sign(compare(a, b)) == -sign(compare(b, a))` for any non-null `a, b`
    3. **Transitivity**: if `compare(a, b) > 0` and `compare(b, c) > 0`, then `compare(a, c) > 0`
    4. **Consistency with equals**: if `compare(a, b) == 0`, then `a.equals(b)` should ideally hold (or at least be documented)
  - The test should create two distinct but equal-in-comparison objects and verify that `compare(a, a) == 0` AND `compare(a, b) == 0` AND `compare(b, a) == 0` — a violation here (e.g., `compare(a, b)` returning non-zero when `equals` returns true, or `compare(a, a)` returning non-zero) indicates a bug.

- WHEN the TG encounters any class overriding `compareTo` or `equals` on mutable fields (fields that change after object creation, like timestamps, device IDs, or status flags):
  - THEN it should test with objects where these fields are identical AND where they differ, verifying consistent ordering in both cases.
  - Include a specific test case: create two objects with identical fields (same device ID, same timestamp, same status), then assert `comparator.compare(obj1, obj2) == 0` and `comparator.compare(obj1, obj1) == 0`.

- Common pitfalls to avoid:
  - Testing only the happy path (e.g., only comparing different objects) — always test self-comparison (reflexivity)
  - Assuming that because `equals` returns true, the comparator returns 0 — verify explicitly
  - Writing tests that only check ordering when fields differ, missing bugs where equal objects are mis-ordered
  - Forgetting to test null-safety if the comparator does not document that nulls are not allowed

- **Correct test example** (for a position object with compareTo):
  ```java
  @Test
  public void testComparatorConsistency() {
      Position p1 = new Position();
      p1.setDeviceId(1);
      p1.setFixTime(new Date(1000));
      p1.setValid(true);
      
      Position p2 = new Position();
      p2.setDeviceId(1);
      p2.setFixTime(new Date(1000));
      p2.setValid(true);
      
      // Reflexivity
      assertEquals(0, p1.compareTo(p1));
      assertEquals(0, p2.compareTo(p2));
      
      // Consistency for equal objects
      assertEquals(0, p1.compareTo(p2));
      assertEquals(0, p2.compareTo(p1));
  }
  ```

- **Incorrect test example** (too narrow, misses the bug):
  ```java
  @Test
  public void testComparatorOrdering() {
      Position p1 = new Position();
      p1.setDeviceId(1);
      p1.setFixTime(new Date(1000));
      
      Position p2 = new Position();
      p2.setDeviceId(2);
      p2.setFixTime(new Date(2000));
      
      // Only tests ordering with different values — does NOT catch reflexivity/consistency bugs
      assertTrue(p1.compareTo(p2) != 0);
  }
  ```