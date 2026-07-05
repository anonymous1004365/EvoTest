---
name: duration-toString-rounding-errors
description: When testing time-to-string conversion methods that divide milliseconds
  into larger units, verify boundary values where integer division truncation produces
  unexpected zero values, such as 1 millisecond displaying as "0 milliseconds".
code_tags:
- WRITE_CONVERSION
- ARITHMETIC_OVERFLOW
- BOUNDARY_CHECK
- ROUNDING
test_pattern: PARAMETRIC_TEST
---

# duration-toString-rounding-errors

## Instructions

# Duration toString Rounding Errors

## Instructions

- WHEN the TG encounters a Duration, time-interval, or time-value class that converts internal millisecond or nanosecond values to human-readable string representations (e.g., `toString()`, `toString(Locale)`)
- THEN the TG should write PARAMETRIC_TEST tests that exercise boundary values where integer division truncation could produce incorrect results. Include:
  - The smallest non-zero value (e.g., 1 millisecond) — verify it is rendered as `"1 millisecond"` not `"0 milliseconds"` or `"1 milliseconds"`
  - Values just below each unit boundary (e.g., 999 milliseconds = `"999 milliseconds"`, not `"0 seconds"`)
  - The exact unit boundary (e.g., 1000 milliseconds = `"1 second"`, 60000 milliseconds = `"1 minute"`)
  - Values just above each unit boundary (e.g., 1001 milliseconds = `"1 second"`)
  - Mixed-unit representations if the API supports them (e.g., 3661000 milliseconds = `"1 hour 1 minute 1 second"`)
  - Negative values if supported by the API
  - Use the specific Locale-dependent overload `toString(Locale)` when applicable, testing both default and explicit locale (e.g., `Locale.ENGLISH`, `Locale.GERMAN`)
  - Verify the test fails on the buggy version by asserting the expected string (e.g., `assertEquals("1 millisecond", duration.toString())`) and checking for the specific error message pattern
- Common pitfalls to avoid:
  - Testing only round millisecond values (1000, 2000, 60000) — these pass but miss the boundary truncation bug
  - Assuming that integer division of milliseconds into units (seconds, minutes, hours) always rounds correctly — use `Math.round()` or add half-unit before division to avoid truncation
  - Forgetting that the plural/singular form depends on the unit value — 1 millisecond should be singular, 2+ should be plural
  - Not testing with the smallest possible non-zero Duration (1 millisecond) which is most likely to expose truncation

### Correct Example (catches the bug)
```java
@Test
public void toStringOneMillisecond()
{
    Duration duration = Duration.milliseconds(1);
    assertEquals("1 millisecond", duration.toString());
}

@Test
public void toStringBoundaryValues()
{
    assertEquals("0 milliseconds", Duration.milliseconds(0).toString());
    assertEquals("1 millisecond", Duration.milliseconds(1).toString());
    assertEquals("999 milliseconds", Duration.milliseconds(999).toString());
    assertEquals("1 second", Duration.milliseconds(1000).toString());
    assertEquals("1001 milliseconds", Duration.milliseconds(1001).toString());
    assertEquals("59 seconds", Duration.milliseconds(59000).toString());
    assertEquals("1 minute", Duration.milliseconds(60000).toString());
    assertEquals("1 minute 1 second", Duration.milliseconds(61000).toString());
}
```

### Incorrect Example (misses the bug)
```java
@Test
public void toStringBasic()
{
    // Only tests round values — does not expose truncation bug for 1 millisecond
    assertEquals("0 milliseconds", Duration.milliseconds(0).toString());
    assertEquals("1000 milliseconds", Duration.milliseconds(1000).toString());
    assertEquals("1 second", Duration.milliseconds(1000).toString());
}
```