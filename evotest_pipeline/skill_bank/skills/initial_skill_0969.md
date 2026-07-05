---
name: marker-hasparents-null-safety
description: When testing methods like hasParents() on a Marker with added then removed
  parents, the test must verify that hasParents() correctly returns false after removing
  all parents instead of throwing a NullPointerException. This skill prevents NPEs
  from unsynchronized access to volatile Marker arrays.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: STATE_TEST
---

# marker-hasparents-null-safety

## Instructions

# Marker hasParents Null Safety After Removing All Parents

## Instructions

WHEN the TG encounters a `Marker` implementation (such as `MarkerManager.Log4jMarker`) where `hasParents()` accesses a volatile `Marker[] parents` field without synchronization, and `remove(Marker)` sets `parents = null` inside a `synchronized` block:

- THEN the TG MUST test that after adding a parent Marker then removing it, calling `hasParents()` returns `false` without throwing a `NullPointerException`.
- The TG should use `MarkerManager.getMarker("name")` to create markers and `marker.addParents(parentMarker)` to add a parent, then `marker.remove(parentMarker)` to remove the parent.
- The test must verify that `hasParents()` returns `false` after all parents are removed and that no `NullPointerException` is thrown.
- Use `assertFalse(marker.hasParents())` to assert the expected state.

Common pitfalls to avoid:
- Testing only the `contains()` or `isInstanceOf()` behavior without testing `hasParents()` after removal.
- Assuming that since `remove()` succeeded, `hasParents()` is safe to call.
- Not testing the specific sequence: create marker → add parent → remove parent → check hasParents().
- Testing in a single-threaded context only (the race condition is real but the basic NPE from null array access should be tested even single-threaded).

### Correct example:
```java
final Marker marker = MarkerManager.getMarker("A");
final Marker parent = MarkerManager.getMarker("P");
marker.addParents(parent);
assertTrue(marker.hasParents());
marker.remove(parent);
assertFalse(marker.hasParents()); // No NPE
```

### Incorrect example:
```java
final Marker marker = MarkerManager.getMarker("A");
final Marker parent = MarkerManager.getMarker("P");
marker.addParents(parent);
marker.remove(parent);
// Missing: assertFalse(marker.hasParents());
// This misses the NPE bug entirely
```