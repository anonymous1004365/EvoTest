---
name: date-converter-locale-mutation
description: When a date/time converter performs locale-specific formatting, the test
  must verify that calling convertToString with one locale does not mutate the internal
  formatter's locale, causing incorrect output for subsequent calls with a different
  locale. Test multiple locales in sequence.
code_tags:
- VALIDATION
- LOCALE_INDEPENDENT_FORMATTING
- STATE_MUTATION
test_pattern: STATE_TEST
---

# date-converter-locale-mutation

## Instructions

# Date Converter Locale Mutation Testing

## Instructions

- WHEN the TG encounters a date/time converter class (such as `AbstractDateConverter`, `AbstractJavaTimeConverter`, `DateConverter`, `LocalDateConverter`, `LocalTimeConverter`, `LocalDateTimeConverter`, `ZonedDateTimeConverter`) that caches or obtains a `DateTimeFormatter` or `DateFormat` instance that is subsequently mutated by calling methods like `withLocale()` or `setLenient()`
- THEN the TG should write a **state test** that:
  1. Creates a single converter instance
  2. Calls `convertToString()` (or `convertToObject()`) with one `Locale` (e.g., `Locale.GERMAN`)
  3. Then calls `convertToString()` with a **different** `Locale` (e.g., `Locale.US`)
  4. Asserts that the result for the **first** locale is still correct when the method is called again with that first locale
  5. Also asserts both results are correct for their respective locales (e.g., "03.07.2025" for German vs "07/03/2025" for US)

- The test should specifically verify that the converter does **not** permanently mutate a cached formatter's locale when formatting for a different locale. A common bug is that `DateTimeFormatter.withLocale()` creates a **new** formatter but the converter stores it back into the cached field, overwriting the original.

- **Common pitfalls to avoid:**
  - Testing with only a single locale (won't catch cross-locale mutation bugs)
  - Testing locale-specific formatting only on a freshly-created converter (the bug only manifests when the converter is reused with different locales)
  - Assuming `DateTimeFormatter.withLocale()` is immutable in the sense that it doesn't mutate the original — it does return a new instance, but if the converter assigns the result back to its cached field, the original locale is lost
  - Not testing both directions (A→B then B→A) to prove no mutation

- **Example of a good test (catching the bug):**
```java
@Test
public void convertToString_LocaleNotMutated()
{
    LocalDateConverter converter = new LocalDateConverter();
    LocalDate date = LocalDate.of(2025, 7, 3);

    // First call with German locale
    String germanResult = converter.convertToString(date, Locale.GERMAN);

    // Second call with US locale — this MUST NOT mutate the cached formatter
    String usResult = converter.convertToString(date, Locale.US);

    // Verify both results are correct
    assertEquals("03.07.2025", germanResult);
    assertEquals("07/03/2025", usResult);

    // Verify that calling with German locale again still works
    String germanResult2 = converter.convertToString(date, Locale.GERMAN);
    assertEquals("03.07.2025", germanResult2);
}
```

- **Example of a weak test (missing the bug):**
```java
@Test
public void convertToString_GermanLocale()
{
    LocalDateConverter converter = new LocalDateConverter();
    LocalDate date = LocalDate.of(2025, 7, 3);
    // Only tests one locale — cannot detect mutation
    assertEquals("03.07.2025", converter.convertToString(date, Locale.GERMAN));
}
```