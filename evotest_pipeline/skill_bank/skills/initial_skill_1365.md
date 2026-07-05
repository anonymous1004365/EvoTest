---
name: build-timestamp-format-timezone-calendar-setup
description: When testing date/time formatting using SimpleDateFormat with a UTC TimeZone,
  ensure that the GregorianCalendar instance used by the format is the system default,
  not explicitly set to a GregorianCalendar that may have a different TimeZone. Without
  this, the TimeZone set via setTimeZone() may be overridden by the calendar's own
  zone, causing hour-offset bugs.
code_tags:
- STATE_MUTATION
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# build-timestamp-format-timezone-calendar-setup

## Instructions

# Build Timestamp Format Timezone Calendar Setup

## Instructions

- WHEN the TG encounters code that creates a `SimpleDateFormat` and calls both `setCalendar(...)` and `setTimeZone(...)` on it — THEN the TG should verify that the `setTimeZone()` call is made AFTER `setCalendar()`, because `setCalendar()` replaces the entire calendar object and its associated timezone, potentially overwriting any timezone set earlier.

- WHEN the TG is testing code that uses `SimpleDateFormat` with a `GregorianCalendar` (e.g., `dateFormat.setCalendar(new GregorianCalendar())`) followed by `dateFormat.setTimeZone(DEFAULT_BUILD_TIME_ZONE)` — THEN the TG should create a test that formats the same `Date` value using:
  1. The code-under-test's format method
  2. A reference `SimpleDateFormat` created with the same pattern string and timezone set via `setTimeZone()` only (no `setCalendar()` call)
  and assert that both produce identical output.

- WHEN the TG notices that `SimpleDateFormat.setCalendar(...)` is called with a freshly constructed `new GregorianCalendar()` (which has the JVM's default timezone) — THEN the TG should be suspicious that the subsequent `setTimeZone(UTC)` may not take effect, because `GregorianCalendar` has its own timezone field that can override what was set on the `SimpleDateFormat`. The correct practice is either: (a) set the calendar's timezone before passing it, e.g., `new GregorianCalendar(UTC)`, or (b) call `setTimeZone()` after `setCalendar()`.

- WHEN constructing a test for timestamp formatting — THEN include test values that straddle midnight in UTC (e.g., 1:16 AM Berlin local time = 23:16 UTC previous day, and 1:16 AM UTC itself at different points in the year) to catch timezone-dependent off-by-hour errors. Also test both AM and PM hours in 12-hour clock terms to ensure 24-hour format (`HH`) is used, not `hh` (12-hour).

- Common pitfalls to avoid:
  - Testing only one point in time that happens to produce the same result in both the buggy and correct implementations.
  - Assuming `SimpleDateFormat.setTimeZone()` always takes precedence over the calendar's timezone without checking the order of operations or whether `setCalendar()` was called.
  - Not testing across DST transitions or across different months when UTC offsets might differ due to daylight saving in the local default timezone.
  - Testing only with the system clock's current time rather than with fixed, known `Date` values.

### Correct Example (detects the bug)

```java
Calendar cal = Calendar.getInstance();
cal.setTimeZone(MavenBuildTimestamp.DEFAULT_BUILD_TIME_ZONE);
cal.set(Calendar.HOUR_OF_DAY, 0);
cal.set(Calendar.MINUTE, 16);
cal.set(Calendar.SECOND, 0);
cal.set(Calendar.YEAR, 1976);
cal.set(Calendar.MONTH, Calendar.NOVEMBER);
cal.set(Calendar.DATE, 11);
Date firstTestDate = cal.getTime();

cal.set(Calendar.HOUR_OF_DAY, 23);
Date secondTestDate = cal.getTime();

SimpleDateFormat format =
    new SimpleDateFormat(MavenBuildTimestamp.DEFAULT_BUILD_TIMESTAMP_FORMAT);
format.setTimeZone(MavenBuildTimestamp.DEFAULT_BUILD_TIME_ZONE);
assertEquals("1976-11-11T00:16:00Z", format.format(firstTestDate));
assertEquals("1976-11-11T23:16:00Z", format.format(secondTestDate));
```

### Incorrect Example (would NOT detect the bug)

```java
// This test uses the MavenBuildTimestamp constructor directly which calls
// setCalendar(new GregorianCalendar()) THEN setTimeZone(UCT).
// The test doesn't know what timezone the JVM default GregorianCalendar has,
// so it can't detect the hour discrepancy.
MavenBuildTimestamp ts = new MavenBuildTimestamp(firstTestDate);
assertEquals("1976-11-11T00:16:00Z", ts.formattedTimestamp());  // might fail depending on JVM locale
```