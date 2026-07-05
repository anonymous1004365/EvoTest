---
name: timestamp-filter-range-validation
description: When testing TimestampFilter initialization with date string parameters,
  test that the init() method correctly parses all date formats (yyyyMMddHHmmssz)
  and use LONG prefix format. Catch ParseException from invalid dates during initialization.
code_tags:
- VALIDATION
- INPUT_PARSE_EXCEPTION
test_pattern: EXCEPTION_TEST
---

# timestamp-filter-range-validation

## Instructions

# Timestamp Filter Range Parameter Validation

## Instructions

- WHEN the TG encounters `TimestampFilter.init()` being called with date string options (the "start" and "end" options), or the `setStart()`, `setEnd()`, `setRange()` static convenience methods
- THEN it should test that these methods correctly parse the `yyyyMMddHHmmssz` date format and also handle the `LONG` prefix format (e.g., `LONG100000101000000`). The TG should test:
  1. That passing an invalid date string (e.g., `"100000101000000GMT"`) to the "start" or "end" option via `IteratorSetting.addOption()` and then calling `TimestampFilter.init()` throws an `IllegalArgumentException`. The `init()` method wraps any `ParseException` in an `IllegalArgumentException`.
  2. That passing a valid date string in `yyyyMMddHHmmssz` format (e.g., `"20100101000000GMT"`) to `init()` works correctly and sets the start/end timestamp.
  3. That passing a valid `LONG` prefixed value (e.g., `"LONG1262304000000"`) to `init()` works correctly.
  4. That `validateOptions(Map<String,String>)` returns `false` when given an invalid date string for "start" or "end".

- Common pitfalls to avoid:
  - Testing only the `setStart()`/`setEnd()` convenience methods — also test `init()` directly with options, since the convenience methods throw `IllegalArgumentException` with a message while `init()` wraps the `ParseException`.
  - Forgetting to handle the `LONG` prefix format — always test both the date format and the `LONG` format.
  - Not verifying the `ParseException` is properly caught and wrapped as `IllegalArgumentException` in `init()` vs. rethrown as is in `setStart()`/`setEnd()`.

- Example of testing `init()` with invalid date:
```java
@Test(expected = IllegalArgumentException.class)
public void testTimestampFilterInvalidDate() throws IOException {
    IteratorSetting is = new IteratorSetting(1, TimestampFilter.class);
    is.addOption(TimestampFilter.START, "100000101000000GMT");
    TimestampFilter filter = new TimestampFilter();
    filter.init(new SortedMapIterator(new TreeMap<Key,Value>()), is.getOptions(), null);
}
```

- Example of testing `validateOptions()` with invalid date (should return false, not throw):
```java
@Test
public void testTimestampFilterValidateInvalid() {
    IteratorSetting is = new IteratorSetting(1, TimestampFilter.class);
    is.addOption(TimestampFilter.START, "100000101000000GMT");
    TimestampFilter filter = new TimestampFilter();
    assertFalse(filter.validateOptions(is.getOptions()));
}
```

- Example of testing with a valid date:
```java
@Test
public void testTimestampFilterValidDate() throws IOException {
    IteratorSetting is = new IteratorSetting(1, TimestampFilter.class);
    is.addOption(TimestampFilter.START, "20100101000000GMT");
    TimestampFilter filter = new TimestampFilter();
    filter.init(new SortedMapIterator(new TreeMap<Key,Value>()), is.getOptions(), null);
}
```