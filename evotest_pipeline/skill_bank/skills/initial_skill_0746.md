---
name: number-currency-format-roundtrip
description: WHEN a numeric converter (like FloatConverter, DoubleConverter, BigDecimalConverter)
  is tested with a custom NumberFormat (e.g. currency format), THEN the test MUST
  verify that convertToObject(convertToString(value)) produces the same value, detecting
  broken roundtrip parsing. This skill specifically addresses the bug where `parse()`
  in AbstractNumberConverter performs regex replaceAll on a String value (converting
  spaces to non-breaking spaces) but the custom NumberFormat's parse() method cannot
  handle the result because it expects the original formatting.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# number-currency-format-roundtrip

## Instructions

# Number/Currency Format Roundtrip Test

## Instructions

WHEN a numeric converter (subclass of `AbstractNumberConverter` or `AbstractDecimalConverter`) is configured with a custom `NumberFormat` (e.g., `NumberFormat.getCurrencyInstance(locale)`) rather than `NumberFormat.getInstance(locale)`:

- THEN the TG should write a **roundtrip test** that:
  1. Creates the converter instance with the custom `NumberFormat` override (via anonymous subclass overriding `newNumberFormat()`)
  2. Calls `convertToString()` with a numeric value (e.g., `Float.valueOf(1234f)`) and `Locale.FRENCH` (or another locale producing grouping separators)
  3. Captures the resulting string
  4. Calls `convertToObject()` with that string and the same locale
  5. Asserts that the result equals the original numeric value

- WHEN the bug is present, the roundtrip test will fail with a `ConversionException` wrapping a `ParseException` because:
  - `AbstractNumberConverter.parse()` does `((String)value).replaceAll("(\\d+)\\s(?=\\d)", "$1\u00A0")` on the input string
  - But a custom `NumberFormat` (e.g., currency format) already uses the locale-appropriate non-breaking space (U+00A0) in its output
  - The regex conversion trying to "fix" the string actually corrupts it, making it unparseable

- The TG MUST test with at least these values:
  - A value >= 1000 (to trigger the grouping separator/thousands separator)
  - At least two different locales: one that uses space as group separator (like `Locale.FRENCH`) and one that uses comma (like `Locale.US`)
  
- Common pitfalls to avoid:
  - ❌ Testing only with `NumberFormat.getInstance(locale)` — this does NOT trigger the bug because standard number formats handle the non-breaking space correctly
  - ❌ Testing only with values < 1000 — the grouping separator only appears for values >= 1000 (e.g., 1234 becomes "1 234" but 123 becomes just "123")
  - ❌ Testing only one direction (convertToString OR convertToObject) — the bug manifests as a broken roundtrip, so both directions must be tested together
  - ❌ Not catching `ConversionException` explicitly — the test should expect `convertToObject()` to throw or should assert the parsed value

### Correct test pattern:
```java
// Create a converter with custom NumberFormat (e.g., currency format)
FloatConverter fc = new FloatConverter() {
    private static final long serialVersionUID = 1L;

    @Override
    protected NumberFormat newNumberFormat(Locale locale) {
        return NumberFormat.getCurrencyInstance(locale);
    }
};

// Test roundtrip with a value that uses grouping separator
String string = fc.convertToString(Float.valueOf(1234f), Locale.FRENCH);
assertEquals(Float.valueOf(1234f), fc.convertToObject(string, Locale.FRENCH));
```

### Incorrect test patterns to avoid:
```java
// WRONG: Only tests standard number format, doesn't test custom format
FloatConverter fc = new FloatConverter();
assertEquals(Float.valueOf(1234f), fc.convertToObject("1 234", Locale.FRENCH));

// WRONG: Only tests convertToString direction
FloatConverter fc = new FloatConverter();
String result = fc.convertToString(Float.valueOf(1234f), Locale.FRENCH);
assertEquals("1 234,00", result);

// WRONG: Tests value < 1000 (no grouping separator triggered)
FloatConverter fc = new FloatConverter() {
    @Override
    protected NumberFormat newNumberFormat(Locale locale) {
        return NumberFormat.getCurrencyInstance(locale);
    }
};
assertEquals(Float.valueOf(123f), fc.convertToObject(fc.convertToString(123f, Locale.FRENCH), Locale.FRENCH));
```