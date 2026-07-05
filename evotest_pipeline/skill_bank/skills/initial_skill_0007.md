---
name: datepicker-timezone-type-conversion
description: When testing date/time picker components that serialize dates to strings
  in JavaScript (Date(...) constructor), the test must verify timezone-aware conversion
  correctly formats dates across different source timezones. This skill ensures date
  formatting converts properly and handles type conversion from DateTimeZone to string.
code_tags:
- TYPE_CONVERSION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# datepicker-timezone-type-conversion

## Instructions

# DatePicker TimeZone Type Conversion Validation

## Instructions

- WHEN the TG encounters code that formats dates as JavaScript `Date(...)` strings (e.g., generating `"Date(year, month, day)"` from a Date object or locale data)
- THEN the TG should write a parametric-style test that:
  1. Creates `Date` objects with different source timezones (e.g., `DateTimeZone.UTC`, `DateTimeZone.forID("America/New_York")`, `DateTimeZone.forID("Europe/Paris")`)
  2. Converts dates through the picker's formatting/rendering pipeline
  3. Asserts that the generated JavaScript date string correctly reflects the target timezone conversion (not just the local time of the JVM)
  4. Specifically verifies that the **day/month/year components** in the output string match the expected values **after timezone conversion**, not before
- The test should expect a test failure (e.g., off-by-one day or hour) when the buggy version doesn't properly handle the timezone conversion from different source zones
- Common pitfalls:
  - Testing only with the JVM's default timezone (which may accidentally pass)
  - Asserting the raw Date values without considering timezone offset
  - Testing only UTC dates and missing non-UTC source timezones that cross date boundaries (e.g., midnight → previous day)
  - Forgetting that `Date(year, month, day)` in JavaScript expects month as 0-indexed

### Example

**Correct test approach (parametric, multiple zones):**
```java
// Test with multiple DateTimeZones to catch conversion bugs
DateTimeZone[] zones = {
    DateTimeZone.UTC,
    DateTimeZone.forID("America/New_York"),
    DateTimeZone.forID("Europe/Paris")
};

for (DateTimeZone zone : zones) {
    // Create a Date that crosses midnight when converted
    DateTime dt = new DateTime(2020, 6, 15, 23, 30, zone);
    // Expected: if converting to UTC, this might be June 16, 2020
    String output = picker.formatDate(dt.toDate());
    // Verify the output matches expected timezone-converted values
    assertTrue("Failed for zone: " + zone, 
        output.contains("2020") && output.contains("6"));
}
```

**Incorrect test (only tests JVM default timezone, misses conversion bug):**
```java
// BAD: Only uses default timezone, won't catch timezone conversion issues
Date date = new Date(120, 5, 15); // June 15, 2020
String output = picker.formatDate(date);
assertEquals("Date(2020, 5, 15)", output);
```

**Incorrect test (comparing raw millis without timezone conversion):**
```java
// BAD: Doesn't verify the string output after timezone conversion
assertNotNull(picker.formatDate(someDate));
```