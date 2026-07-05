---
name: date-field-treatment-mismatch
description: When components or converters directly read Date fields (year/month/day)
  from a java.util.Date object using deprecated getYear()/getMonth()/getDate(), test
  that passing Dates created from a java.util.Calendar (which correctly treats month
  0=January) produces the same result as passing Dates created from year-month-day
  constructors (which may have different offset behavior). The bug causes date field
  extraction to be off by one in the year/month/day when the Date was built from a
  Calendar.
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# date-field-treatment-mismatch

## Instructions

# Skill: Test Date Field Treatment Across Different Date Construction Methods

## Instructions

- WHEN the TG encounters code that extracts individual date fields (year, month, day of month) from a `java.util.Date` object using methods such as `getYear()`, `getMonth()`, `getDate()`, or uses `Calendar.setTime(date)` followed by `Calendar.get(field)` to retrieve these fields
- THEN the TG should write tests that construct `java.util.Date` objects in **two different ways** and verify the extracted fields match:
  1. Using the **deprecated `Date(int year, int month, int day)` constructor** (e.g., `new Date(114, 5, 11)` for June 11, 2014) — note that year=114 means 2014, month=5 means June (0-indexed).
  2. Using a **`java.util.Calendar` instance** (e.g., `Calendar cal = Calendar.getInstance(); cal.set(2014, Calendar.JUNE, 11); Date date = cal.getTime()`) — note that `Calendar.JUNE` is also 0-indexed (value=5), but the resulting `Date` object may differ in internal representation.
- The test should verify that the extracted date fields (year, month, day) are **identical** regardless of how the `Date` object was constructed, especially when the Date is then passed to the component under test.
- **Common pitfall**: Testing only with `Date` objects created via constructors. The bug surfaces when a `Date` is created from a `Calendar` (e.g., via a date model that uses `Calendar.getTime()`) and the component treats it differently than a constructor-built Date.
- **Example correct test pattern**:
  ```java
  // Test with Date created from Calendar
  Calendar cal = Calendar.getInstance();
  cal.set(2014, Calendar.JUNE, 11);
  Date calendarDate = cal.getTime();
  
  // Test with Date created from constructor
  Date constructorDate = new Date(114, 5, 11); // June 11, 2014
  
  // Both should produce same extracted fields
  // e.g., year=114, month=5, date=11
  ```
- **Expected failure on buggy version**: The component under test produces different year/month/day values for the two Date objects, even though both represent the same calendar date. For example, one might produce year=114 while the other produces year=115 (off-by-one in year), or month=5 vs month=6 (off-by-one in month).
- **What to assert**: Assert that both inputs produce the same formatted output string or the same extracted field values from the component.