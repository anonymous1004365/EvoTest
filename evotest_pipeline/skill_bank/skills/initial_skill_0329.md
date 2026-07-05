---
name: time-getHour-24-hour-clock
description: When testing time objects with getHour() methods that may use 12-hour
  AM/PM formatting instead of 24-hour military clock, verify that PM hours (1-11PM)
  return correct values (13-23) rather than 12-hour values. This applies especially
  to Wicket's Time.getHour() method which delegates to Java's date/time formatting.
code_tags:
- TYPE_CONVERSION
- HOUR_FORMAT_12_24_CLOCK
test_pattern: STATE_TEST
---

# time-getHour-24-hour-clock

## Instructions

# Time getHour() Must Return 24-Hour Clock Values

## Instructions

- WHEN the TG encounters a class (e.g., `org.apache.wicket.util.time.Time`) that has a `getHour()` method returning an `int` representing the hour of the day, and this method internally uses Java's date/time formatting APIs (e.g., `SimpleDateFormat`, `DateTimeFormatter`, or `Calendar.get(Calendar.HOUR)` instead of `Calendar.HOUR_OF_DAY`)
- THEN the TG should test that `getHour()` returns the correct 24-hour clock value for PM times (e.g., 9 PM = 21, not 9). Write a test that:
  1. Creates a `Time` instance for an afternoon/evening time where the hour is clearly in the PM range (e.g., 9:00 PM, 1:00 PM, 11:30 PM)
  2. Asserts that `getHour()` returns the 24-hour clock value (e.g., 21 for 9 PM, 13 for 1 PM, 23 for 11:30 PM)
  3. The test should fail on the buggy version with an assertion error showing the 12-hour value instead of the 24-hour value
- Include concrete values: for a `Time` representing 9:00 PM, expect `assertEquals(21, time.getHour())`; for 1:00 PM, expect `assertEquals(13, time.getHour())`
- **Common pitfalls to avoid:**
  - Testing only AM times (e.g., midnight, 9 AM) — these are the same on both 12-hour and 24-hour clocks, so the bug won't be detected
  - Testing hours 1 PM-11 PM where the 12-hour and 24-hour values differ
  - Using `Calendar.HOUR` (0-11) instead of `Calendar.HOUR_OF_DAY` (0-23) in the date construction helper
  - Testing with `SimpleDateFormat` pattern `"hh"` (1-12) instead of `"HH"` (0-23) in the conversion logic

## Example

**Correct test (catches the bug):**
```java
// WICKET-5442 getHour() should be on 24-hour clock
Calendar calendar = Calendar.getInstance();
calendar.set(2015, Calendar.JANUARY, 1, 21, 0, 0); // 9:00 PM
Time time = Time.valueOf(calendar.getTime());
assertEquals(21, time.getHour()); // 9 PM = 21, NOT 9
```

**Incorrect test (may not catch the bug):**
```java
// Only tests AM hours — same on both clocks
Calendar calendar = Calendar.getInstance();
calendar.set(2015, Calendar.JANUARY, 1, 9, 0, 0); // 9:00 AM
Time time = Time.valueOf(calendar.getTime());
assertEquals(9, time.getHour()); // 9 AM = 9 on both clocks — no bug detected
```