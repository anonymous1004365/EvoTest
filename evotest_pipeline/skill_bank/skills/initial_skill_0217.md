---
name: null-marker-removal-state-validation
description: When a collection maintains internal state that can become inconsistent
  after removing null elements, the test must verify both the removal API handles
  null gracefully and the internal state remains consistent.
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# null-marker-removal-state-validation

## Instructions

# Null Marker Removal State Validation

## Instructions

**WHEN** the TG encounters a `MarkerManager` (or similar manager) that stores markers in a data structure (e.g., `Map<String, Marker>`) and provides a `remove(Marker)` method, and the code's `remove` implementation calls `marker.getName()` on the argument without checking if the argument is null:

- **THEN** the TG should write a test that calls `remove(null)` directly (not via a marker name lookup) and verifies that a `NullPointerException` is not thrown — i.e., the method should gracefully handle null input by returning false or no-oping, rather than crashing.

- **THEN** the TG should additionally verify that after calling `remove(null)`, the manager's internal state (e.g., the `Marker` returned by `getMarker("test")`) remains unchanged and consistent.

- **THEN** the TG should ensure the test uses the concrete `MarkerManager` class's `remove(Marker)` method (signature: `public synchronized boolean remove(final Marker marker)`) rather than any deprecated `remove(String)` method.

- **Common Pitfall**: Do NOT test only the `remove(String)` method (deprecated) or only the return value of `remove(null)` without also verifying that the internal state (stored markers in the map) remains consistent.

**Example — Correct test:**

```java
@Test
public void testRemoveNullMarker() {
    final MarkerManager.Marker marker = MarkerManager.getMarker("testRemoveMarker");
    assertNotNull("Marker should not be null", marker);
    
    // Remove null marker — should not throw NPE
    assertFalse("remove(null) should return false", MarkerManager.remove(null));
    
    // Verify marker still exists in the manager after the invalid removal
    final Marker retrieved = MarkerManager.getMarker("testRemoveMarker");
    assertSame("Marker should still be available", marker, retrieved);
}
```

**Example — Incorrect test (misses the bug):**

```java
@Test
public void testRemoveNullMarker() {
    // This only tests remove(String) — not remove(Marker)
    assertFalse("remove(null) via string should return false", 
        MarkerManager.remove(null, null)); // Wrong method signature
}
```