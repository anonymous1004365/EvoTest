---
name: monthly-rollover-cross-year-boundary
description: WHEN testing PatternProcessor.getNextTime() with monthly frequency (%d{yyyy-MM})
  and the current date is near a year boundary (e.g., December), THEN the test must
  verify that the computed next time correctly advances to the first day of the NEXT
  year (January). Without proper year boundary handling, the increment logic jumps
  to the current year's February instead.
code_tags:
- NULL_CHECK
- VALIDATION
- RESOURCE_MANAGEMENT
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# monthly-rollover-cross-year-boundary

## Instructions

# Monthly Rollover Cross-Year Boundary

## Instructions

- WHEN the TG encounters a `PatternProcessor` initialized with a monthly date pattern such as `"logs/app-%d{yyyy-MM}.log.gz"` (where the frequency is `RolloverFrequency.MONTHLY`), and the `getNextTime(long currentMillis, int increment, boolean modulus)` method is called with a date near a year boundary (e.g., December 31st of any year)
- THEN the TG MUST write a test that sets the `Calendar` to a date in December (e.g., `2014, Calendar.DECEMBER, 31, 10, 31, 59`) and calls `pp.getNextTime(initial.getTimeInMillis(), 1, false)`, then asserts that the returned timestamp corresponds to January 1st of the NEXT year (e.g., `2015/01/01 00:00:00.000`)
- Common pitfalls:
  - Testing only intra-year monthly rollover (e.g., January→February, October→November) without testing the December→January cross-year case
  - Forgetting that `Calendar.DECEMBER` has value 11 (zero-based months), so `Calendar.JANUARY` of the next year is month 0 with year+1
  - Assuming the year is handled correctly by `cal.set(Calendar.MONTH, currentCal.get(Calendar.MONTH))` alone — the bug is that `cal` initializes to January 1st of the current year, then `cal.set(Calendar.MONTH, currentCal.get(Calendar.MONTH))` sets it to December of the current year, and `increment(cal, Calendar.MONTH, 1, false)` rolls it to January but **of the same year** because `cal.set()` does not auto-adjust the year
  - Only testing months that don't cross year boundary (e.g., `initial.set(2014, Calendar.OCTOBER, 15)`, which works fine)

- **Example (correct test that catches the bug):**
  ```java
  @Test
  public void testGetNextTimeMonthlyReturnsFirstDayOfNextYear() {
      final PatternProcessor pp = new PatternProcessor("logs/app-%d{yyyy-MM}.log.gz");
      final Calendar initial = Calendar.getInstance();
      initial.set(2014, Calendar.DECEMBER, 31, 10, 31, 59);
      final long actual = pp.getNextTime(initial.getTimeInMillis(), 1, false);

      final Calendar expected = Calendar.getInstance();
      expected.set(2015, Calendar.JANUARY, 1, 00, 00, 00);
      expected.set(Calendar.MILLISECOND, 0);
      assertEquals(format(expected.getTimeInMillis()), format(actual));
  }
  ```

- **Example (incorrect test that misses the bug):**
  ```java
  @Test
  public void testGetNextTimeMonthlyReturnsFirstDayOfNextMonth() {
      final PatternProcessor pp = new PatternProcessor("logs/app-%d{yyyy-MM}.log.gz");
      final Calendar initial = Calendar.getInstance();
      initial.set(2014, Calendar.OCTOBER, 15, 10, 31, 59); // Oct -> Nov, same year
      final long actual = pp.getNextTime(initial.getTimeInMillis(), 1, false);
      // This passes on both buggy and fixed versions
  }
  ```