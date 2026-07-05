---
name: date-lookup-format-validation
description: When a DateLookup is registered as a lookup plugin in an Interpolator
  and invoked via the Interpolator proxy with a "date:format" prefix pattern, the
  format string after the colon must be correctly passed to DateLookup.lookup(). The
  TG should test this interaction path and ensure the lookup returns a non-null, non-empty
  formatted date string.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: INTERACTION_TEST
---

# date-lookup-format-validation

## Instructions

# Date Lookup Format Validation via Interpolator

## Instructions

WHEN the TG encounters an `Interpolator` class that registers a `DateLookup` instance (e.g., `lookups.put("date", new DateLookup())`) and the lookup resolution logic extracts a prefix and name from a variable string (separated by `:`), THEN the TG should write a test that:

1. **Creates an `Interpolator` with no default lookup** — `new Interpolator()` — which automatically registers the `DateLookup` under the key `"date"`.
2. **Calls `lookup()` with a `"date:<format>"` string**, where `<format>` is a valid `SimpleDateFormat` pattern (e.g., `"yyyy-MM-dd"`).
3. **Asserts that the returned value is not null** — the test should use `assertNotNull("No Date", value)` as the failure message to detect when the lookup returns null on the buggy version.
4. **Asserts that the returned value is not empty** — use `assertFalse(value.isEmpty())` to ensure the formatted date string is produced.
5. **Verifies the returned string matches a known format** — e.g., use `SimpleDateFormat` to format the current date and compare.

The TG should understand that the `DateLookup` itself works correctly when called directly, but the bug may lie in the `Interpolator`'s lookup path, which is the path used in production. Therefore, the `Interpolator` must be the test subject, not the standalone `DateLookup`.

**Common pitfalls:**
- Testing `DateLookup` directly instead of through `Interpolator`. The bug occurs in the `Interpolator.lookup()` method, not in `DateLookup.lookup()`. The test must exercise the `Interpolator` as the lookup entry point.
- Using `assertNotNull` without a custom failure message. The TG should include a descriptive failure message (e.g., `"No Date"`) that matches the actual observed failure.
- Using `assertNull` — the value should not be null; it should be a formatted date string.
- Testing only system property or environment lookups through the `Interpolator` but not the `DateLookup`. The TG should explicitly test `"date:<format>"`.
- Forgetting to test the no-arg `Interpolator()` constructor which registers the lookup. The constructor `Interpolator(StrLookup)` or `Interpolator(Map<String, String>)` may not register `DateLookup`.

**Correct example:**
```java
@Test
public void testLookupWithDefaultInterpolator() {
    final StrLookup lookup = new Interpolator();
    String value = lookup.lookup("date:yyyy-MM-dd");
    assertNotNull("No Date", value);
    assertFalse(value.isEmpty());
    final SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd");
    final String today = format.format(new Date());
    assertEquals(today, value);
}
```

**Incorrect example (won't catch the bug):**
```java
@Test
public void testDateLookupDirectly() {
    final StrLookup lookup = new DateLookup();  // Bug: testing DateLookup directly, not through Interpolator
    String value = lookup.lookup("yyyy-MM-dd");  // Bug: not using "date:" prefix, calling lookup(String) not lookup(LogEvent, String)
    assertNotNull(value);
}
```