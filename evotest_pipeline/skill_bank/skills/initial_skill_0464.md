---
name: marker-setparents-null-reset-bug
description: Use this skill when testing marker hierarchy mutations where a method
  (like setParents) should first clear existing parents before adding new ones, but
  may fail to set the parents field to null when no new parents are passed. This identifies
  state mutation bugs where the internal parents array is not properly reset.
code_tags:
- STATE_MUTATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# marker-setparents-null-reset-bug

## Instructions

# Marker setParents Null Reset Bug

## Instructions

### WHEN the TG encounters a class that manages a mutable internal array state (e.g., `Marker[] parents`) and exposes:
- A `setParents(Marker... markers)` method that is supposed to **replace** all existing parents with new ones
- An `addParents(Marker... parentMarkers)` method that **appends** to existing parents
- A state inspection method (e.g., `hasParents()` or `getParents()`) that checks whether the internal array is non-null

### THEN the TG should:
1. **Test the null/empty case first**: Call `setParents()` with no arguments (empty varargs) or with `setParents((Marker) null)` on a fresh marker that currently has `null` parents.
2. **Verify that `hasParents()` returns false** after calling `setParents()` on a marker that had no parents before.
3. **Test the replacement case**: First add parents, then call `setParents()` with a different set of parents, and verify the old parents are no longer present.
4. **Use `assertFalse()` and `assertTrue()`** to verify the boolean state returned by `hasParents()`.

### Common pitfalls:
- ❌ **Testing only `addParents()` behavior**: The TG might write a test that only verifies parents can be added, but never tests what happens when `setParents()` is called on a marker that currently has no parents (`parents == null`).
- ❌ **Assuming empty varargs is the same as null**: Passing no arguments to `setParents()` (i.e., `setParents()` with empty varargs) should result in `parents` being set to `null`. The bug is that the implementation may leave `parents` as `null` when called with no arguments on an already-null state, but that same code path may fail to update internal bookkeeping.
- ❌ **Not verifying intermediate state**: After calling `setParents()` and before calling `hasParents()`, do not call other mutating methods like `addParents()` that could mask the bug.

### Correct example (MarkerTest.testHasParents):
```java
@Test
public void testHasParents() {
    final Marker parent = MarkerManager.getMarker("PARENT");
    final Marker existing = MarkerManager.getMarker("EXISTING");
    assertFalse(existing.hasParents());  // fresh marker has no parents
    existing.setParents(parent);
    assertTrue(existing.hasParents());   // after setParents, has parents
}
```

### Incorrect approach (would miss the bug):
```java
@Test
public void testSetParents() {
    final Marker parent = MarkerManager.getMarker("PARENT");
    final Marker m = MarkerManager.getMarker("TEST").addParents(parent);
    m.setParents(parent);  // only tests replacement, not the null-initial case
    assertTrue(m.hasParents());
}
```

### Key insight:
The bug manifests when `setParents()` is called on a marker whose `parents` field starts as `null`, and the implementation fails to propagate state updates (like `hasParents()` checking `parents != null`). Always test the null-to-some-parents transition with methods that inspect internal state.