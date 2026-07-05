---
name: null-argument-validation-for-slf4j-marker-bridge
description: When implementing SLF4J Marker bridge methods (add, contains, remove),
  the TG should verify that null arguments consistently throw IllegalArgumentException
  rather than NullPointerException, and that null String arguments to contains(String)
  return false without throwing. The log4j-slf4j-impl Log4jMarker class is a common
  place for such null-handling discrepancies.
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# null-argument-validation-for-slf4j-marker-bridge

## Instructions

# Null Argument Validation for SLF4J Marker Bridge Methods

## Instructions

- WHEN the TG encounters a class that bridges between SLF4J `org.slf4j.Marker` and Log4j `org.apache.logging.log4j.Marker` (e.g., `Log4jMarker` in `log4j-slf4j-impl`)
- THEN it should write tests that verify all public methods accepting SLF4J `Marker` parameters throw `IllegalArgumentException` when passed `null`, and methods accepting `String` parameters handle `null` gracefully without exceptions.

- **For `add(Marker marker)`**: WHEN writing a test for the `add` method, THEN pass `null` as the argument and verify it throws `IllegalArgumentException`. On the buggy version (without null check), this would throw `NullPointerException` from `marker.getName()`.

- **For `contains(Marker marker)`**: WHEN writing a test for `contains(Marker)`, THEN pass `null` as the argument and verify it throws `IllegalArgumentException`. The test should use `Assert.assertFalse(...)` wrapped in a try-catch or use `@Test(expected = IllegalArgumentException.class)`.

- **For `contains(String s)`**: WHEN writing a test for `contains(String)`, THEN pass `null` as the argument and verify it returns `false` (does NOT throw). This differs from `contains(Marker)` in that `null` strings should be handled gracefully.

- **For `remove(Marker marker)`**: WHEN writing a test for the `remove` method, THEN pass `null` as the argument and verify it returns `false` without throwing any exception.

- Common pitfalls to avoid:
  - Do NOT assume that all null-parameter methods throw the same exception — some methods (contains(String), remove(Marker)) are expected to return a default value (`false`) instead of throwing.
  - Do NOT test only one null-dependent method — test ALL public methods that accept parameters: `add`, `contains(Marker)`, `contains(String)`, and `remove`.
  - Do NOT forget to test on the SLF4J bridge (Log4jMarker) directly, not just on the underlying Log4j MarkerManager.Log4jMarker.
  - Do NOT assume the exception message is non-null — the buggy code may throw `IllegalArgumentException` with no message, so use `fail("Expected " + IllegalArgumentException.class.getName())` pattern or `@Test(expected = IllegalArgumentException.class)`.

### Correct Example
```java
@Test
public void testAddNullMarker() {
    final Log4jMarker marker = new Log4jMarker(MarkerManager.getMarker("TEST"));
    final org.slf4j.Marker nullMarker = null;
    try {
        marker.add(nullMarker);
        fail("Expected " + IllegalArgumentException.class.getName());
    } catch (final IllegalArgumentException e) {
        // expected
    }
}
```

### Incorrect Example
```java
// WRONG: uses @Test(expected = NullPointerException.class) instead of IllegalArgumentException
// WRONG: tests only add() but not contains() or remove()
@Test(expected = NullPointerException.class)
public void testAddNullMarker() {
    final Log4jMarker marker = new Log4jMarker(MarkerManager.getMarker("TEST"));
    marker.add(null);  // Will pass on buggy version but fail expectation on fixed version
}
```