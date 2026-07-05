---
name: shallow-copy-shared-mutable-state
description: Detects when shallowCopy() shares mutable internal state (conditions
  Map) between original and copy, and tests that add/remove conditions on one doesn't
  affect the other. Use this skill when testing copy/clone methods on mutable objects.
code_tags:
- STATE_MUTATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# shallow-copy-shared-mutable-state

## Instructions

# Shallow Copy Shared Mutable State

## Instructions

- WHEN the TG encounters a `shallowCopy(String id)` method (or similar clone/copy method) that creates a new object and passes an internal mutable field (e.g., a `Map<Key, Condition>` or `Map<Key, Operation>`) by reference to the new object's constructor
- THEN the TG should write a state test that verifies the side-effect isolation between the original and the copy. Specifically:
  1. Create the original object (e.g., `UpdateOp op1 = new UpdateOp("id", false)`).
  2. Add some state to the original (e.g., `op1.set("p", "value")`).
  3. Create a shallow copy (e.g., `UpdateOp op2 = op1.shallowCopy("id")`).
  4. **Add state to the original AFTER the copy** (e.g., call `op1.containsMapEntry("e", r, true)` to add a condition).
  5. Verify the copy shows the new state — because the internal `conditions` Map is shared by reference.
  6. If the bug is that conditions are `null` in the original (so `getConditions()` returns empty map), the test should assert `assertEquals(0, op2.getConditions().size())` on the first copy (line 194), then `assertEquals(1, op2.getConditions().size())` after adding conditions to `op1` (line 198-199).
- WHEN testing `shallowCopy` but the internal `conditions` field is `null` at the time of the copy
- THEN the test MUST verify that after adding conditions to the original, those conditions become visible through the copy (shared null-to-map mutation), and the test should expect `expected:<1> but was:<0>` failure on the buggy version — this confirms the `conditions` field is shared by reference but not deep-copied.

- Common pitfalls:
  - Testing only the first copy (before adding conditions to the original) and stopping there — this misses the side-effect propagation bug.
  - Assuming `shallowCopy` makes a deep copy of the `conditions` map — it does NOT; it shares the same map (or null) reference.
  - Not initializing the `conditions` map before copying — the shared null reference becomes a non-null map in the original after the copy, and the copy sees the same map via the shared reference.

### Correct example (test that catches the bug):
```java
@Test
public void shallowCopy() {
    UpdateOp op1 = new UpdateOp("id", false);
    op1.set("p", "value");

    UpdateOp op2 = op1.shallowCopy("id");
    assertTrue(op2.hasChanges());
    assertEquals(1, op2.getChanges().size());
    assertEquals(0, op2.getConditions().size());  // conditions is null in op1

    Revision r = Revision.newRevision(1);
    op1.containsMapEntry("e", r, true);  // Now conditions becomes non-null in op1

    op2 = op1.shallowCopy("id");
    assertEquals(1, op2.getConditions().size());  // FAILS on buggy when conditions shared by reference
}
```

### Incorrect example (test that misses the bug):
```java
@Test
public void shallowCopy() {
    UpdateOp op1 = new UpdateOp("id", false);
    op1.set("p", "value");
    
    UpdateOp op2 = op1.shallowCopy("id");
    assertTrue(op2.hasChanges());
    // Only checks the first copy, never adds conditions to original afterward
    // Never tests that conditions added AFTER copy are visible through the copy
}
```