---
name: stat-clear-reset-verification
description: When testing a statistical accumulator that wraps StorelessUnivariateStatistic
  instances, the clear() method must completely reset all state — test that after
  clear(), getMin(), getMax(), getSum() return 0 and getAverage(), getStdDev() return
  NaN. Without this check, a bug where clear() fails to reset the Max internal state
  (leaking the previous max value) goes undetected.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# stat-clear-reset-verification

## Instructions

# Stat Clear() State Reset Verification

## Instructions

- WHEN the TG encounters a class (e.g., `org.apache.accumulo.core.util.Stat`) that wraps multiple `StorelessUnivariateStatistic` instances (`Min`, `Max`, `Sum`, `Mean`, `StandardDeviation`) and exposes a `clear()` method that delegates to each statistic's `clear()`
- THEN it should write a test that:
  1. Creates a `Stat` instance and adds multiple data points (e.g., `{9792, 5933, 4766, 5770, 3763, 3677, 5002}`)
  2. Calls `clear()` on the instance
  3. Verifies that `getMin()`, `getMax()`, and `getSum()` return `0` (the long value `0`)
  4. Verifies that `getAverage()` and `getStdDev()` return `Double.NaN` (use `assertEquals(Double.NaN, stat.getAverage(), 0)`)
- The test should detect that after `clear()`, the buggy version still returns the previous max value (e.g., `9792`) from `getMax()` instead of `0`
- Common pitfalls to avoid:
  - Testing only `getMin()` and `getSum()` but not `getMax()` — the bug is specifically in `Max.clear()` not resetting properly
  - Using a `Stat` with only zeros added (like `zero` in the original test) — the bug only manifests when data has been added with non-zero/multiple values before `clear()`
  - Comparing `stat.getMax()` to `0` with `assertEquals(0, stat.getMax())` without checking it's a `long` — the cast to `long` in `getMax()` returns `0L` for `Double.NaN`-to-long conversion, which happens to pass; verify the value is explicitly `0`
  - Not checking that `getAverage()` and `getStdDev()` return `Double.NaN` after `clear()` — these also depend on internal state being properly reset

### Correct test pattern (isolated):

```java
@Test
public void testClearResetsAllStats() {
    Stat stat = new Stat();
    stat.addStat(9792);
    stat.addStat(5933);
    stat.addStat(4766);
    stat.clear();
    
    assertEquals(0, stat.getMin());
    assertEquals(0, stat.getMax());    // Buggy: returns 9792 instead of 0
    assertEquals(0, stat.getSum());
    assertEquals(Double.NaN, stat.getAverage(), 0);
    assertEquals(Double.NaN, stat.getStdDev(), 0);
}
```

### Incorrect pattern (misses the bug):

```java
@Test
public void testClear() {
    Stat stat = new Stat();
    stat.addStat(0);  // single zero value — doesn't trigger the bug
    stat.clear();
    assertEquals(0, stat.getMin());
    assertEquals(0, stat.getMax());  // passes accidentally
    assertEquals(0, stat.getSum());
}
```