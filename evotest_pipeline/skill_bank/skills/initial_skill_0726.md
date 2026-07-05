---
name: number-conversion-overflow-validation
description: WHEN testing number converters (Long, Integer, etc.) THEN validate that
  converting values outside the target type's range throws ConversionException. This
  skill helps catch missing overflow checks in type conversion implementations.
code_tags:
- OVERFLOW
- VALIDATION
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# number-conversion-overflow-validation

## Instructions

# Number Conversion Overflow Validation

## Instructions

### WHEN the TG encounters a number converter (such as `LongConverter`, `IntegerConverter`, or similar extending `AbstractIntegerConverter`) that uses `NumberFormat` to parse values

**THEN** the TG should verify that:
- The converter throws a `ConversionException` when parsing values outside the range of the target type (e.g., values exceeding `Long.MAX_VALUE` or below `Long.MIN_VALUE` for `LongConverter`)
- Use the converter's `convertToObject(String, Locale)` method directly, passing an out-of-range numeric string
- Assert that a `ConversionException` is thrown with `assertThrows(ConversionException.class, () -> converter.convertToObject(value, Locale.ENGLISH))`

### Common pitfalls to avoid:

1. **Testing only valid values**: Testing only "0", "1", "42" does not exercise overflow paths. You MUST test extreme values like "9223372036854775808" (Long.MAX_VALUE + 1), "18446744073709551616" (overflow), or the negative equivalents.

2. **Testing only the wrong type**: Testing a String like "abc" tests number format errors, NOT overflow. The bug is specifically about values that are validly numeric but exceed the target type's range.

3. **Expecting the wrong exception**: The bug manifests as converting an out-of-range value silently (e.g., wrapping around to a small value) instead of throwing `ConversionException`. Assert specifically for `ConversionException`, not just any `RuntimeException`.

**Wrong approach** (does NOT catch the overflow bug):
```java
@Test
void longConversions_Wrong()
{
    LongConverter converter = new LongConverter();
    // Only tests valid range — misses the overflow bug
    assertThrows(ConversionException.class, () -> converter.convertToObject("abc", Locale.ENGLISH));
}
```

**Correct approach** (catches the overflow bug):
```java
@Test
void longConversions_Correct()
{
    LongConverter converter = new LongConverter();
    Long result = converter.convertToObject("0", Locale.ENGLISH);
    assertEquals(Long.valueOf(0), result);

    // Testing overflow: value larger than Long.MAX_VALUE
    assertThrows(ConversionException.class,
        () -> converter.convertToObject("9223372036854775808", Locale.ENGLISH));

    // Testing underflow: value smaller than Long.MIN_VALUE
    assertThrows(ConversionException.class,
        () -> converter.convertToObject("-9223372036854775809", Locale.ENGLISH));

    // Very large overflow
    assertThrows(ConversionException.class,
        () -> converter.convertToObject("18446744073709551616", Locale.ENGLISH));
}
```

### Additional guidance

- Apply this skill to ALL number converters (Long, Integer, Short, Byte) — any converter whose target type has a defined min/max range
- Use `BigDecimal` or `BigInteger` to construct out-of-range test values if needed, e.g. `BigDecimal.valueOf(Long.MAX_VALUE).add(BigDecimal.ONE).toString()` generates "9223372036854775808"
- The same pattern applies to `IntegerConverter`: test with values like "2147483648" (Integer.MAX_VALUE + 1) and "-2147483649" (Integer.MIN_VALUE - 1)