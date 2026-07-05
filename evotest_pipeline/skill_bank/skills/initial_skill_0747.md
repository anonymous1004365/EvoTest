---
name: custom-level-range-edge-mapping
description: When a JUL-to-Log4j level converter uses a nearest-neighbor search among
  sorted standard levels, custom levels at the extreme ends of the range (e.g., ALL=Integer.MIN_VALUE,
  OFF=Integer.MAX_VALUE) can cause the search loop to return null. This skill teaches
  how to test edge-of-range custom levels.
code_tags:
- LEVEL_RANGE_EDGE
- BOUNDARY_CHECK
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# custom-level-range-edge-mapping

## Instructions

# Custom JUL Level Mapping at Range Edges

## Instructions

WHEN the TG encounters a level converter that maps JUL levels to Log4j levels (e.g., `DefaultLevelConverter`) using a nearest-neighbor search over a sorted list of standard levels (e.g., `ALL`, `FINEST`, `FINER`, `FINE`, `CONFIG`, `INFO`, `WARNING`, `SEVERE`, `OFF`):

- THEN the TG should create a custom JUL level whose intValue() is one greater than `java.util.logging.Level.ALL.intValue()` (which is `Integer.MIN_VALUE`) — e.g., `ALL.intValue() + 1`.
- THEN the TG should verify that `converter.toLevel(customLevel)` returns `Level.ALL`, not `null`.
- THEN the TG should also verify the sanity check: `converter.toLevel(java.util.logging.Level.ALL)` returns `Level.ALL`.
- THEN the TG should similarly test a custom level just below `OFF` (e.g., `OFF.intValue() - 1`) and verify it returns `Level.OFF`.
- THEN the TG should test custom levels one above and one below every other standard level (`FINEST`, `FINER`, `FINE`, `CONFIG`, `INFO`, `WARNING`, `SEVERE`) to ensure the nearest-neighbor loop correctly selects adjacent mapped levels.

Common pitfalls to avoid:
- Testing only String type parameters without testing custom JUL level objects.
- Testing only the standard JUL levels without testing custom levels that are one unit away.
- Not testing the **uppermost and lowermost** range edges (`ALL` and `OFF`) — these are uniquely vulnerable because the nearest-neighbor loop has only one neighbor to compare against, and improper loop termination can return `null`.
- Assuming that `sortedJulLevels` being sorted means the loop safely returns the last/first element without verifying that `prevLevel` is non-null before returning.

### Correct example

```java
static class CustomLevel extends java.util.logging.Level {
    static CustomLevel ALL_P_1 = new CustomLevel("ALL_P_1", java.util.logging.Level.ALL.intValue() + 1);
    static CustomLevel OFF_M_1 = new CustomLevel("OFF_M_1", java.util.logging.Level.OFF.intValue() - 1);
    protected CustomLevel(final String name, final int value) { super(name, value); }
}

@Test
public void testCustomJulLevelNearAll() {
    // Sanity check:
    Assert.assertEquals(Level.ALL, converter.toLevel(java.util.logging.Level.ALL));
    // Test:
    Assert.assertEquals(Level.ALL, converter.toLevel(CustomLevel.ALL_P_1));
}

@Test
public void testCustomJulLevelNearOff() {
    // Sanity check:
    Assert.assertEquals(Level.OFF, converter.toLevel(java.util.logging.Level.OFF));
    // Test:
    Assert.assertEquals(Level.OFF, converter.toLevel(CustomLevel.OFF_M_1));
}
```

### Incorrect example (buggy code would pass this)

```java
@Test
public void testOnlyStandardLevels() {
    // Only tests the mapped levels, NOT custom levels:
    Assert.assertEquals(Level.ALL, converter.toLevel(java.util.logging.Level.ALL));
    Assert.assertEquals(Level.OFF, converter.toLevel(java.util.logging.Level.OFF));
    // This misses the bug entirely because ALL_P_1 returns null on buggy code!
}
```