---
name: min-max-value-boundary-testing
description: When a utility method returns minimum/maximum values for numeric types,
  test that Float.MIN_VALUE and Double.MIN_VALUE are NOT confused with their negative
  maximums. The minimum value of a floating-point type should be -Float.MAX_VALUE/-Double.MAX_VALUE,
  not Float.MIN_VALUE/Double.MIN_VALUE.
code_tags:
- BOUNDARY_CHECK
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# min-max-value-boundary-testing

## Instructions

# Minimum/Maximum Value Boundary Testing for Numeric Types

## Instructions

- WHEN the TG encounters a method that returns the minimum or maximum value for a given numeric type (e.g., `getMinValue(Class<? extends Number> numberType)` or `getMaxValue(Class<? extends Number> numberType)`):
  - THEN the TG should test ALL supported numeric types: `Integer.class`, `int.class`, `Long.class`, `long.class`, `Float.class`, `float.class`, `Double.class`, `double.class`, `Byte.class`, `byte.class`, `Short.class`, `short.class`, as well as non-standard numeric types like `BigDecimal.class`, `BigInteger.class`, and `null`.
  - For `getMinValue(Float.class)`, verify the result equals `-Float.MAX_VALUE` (not `Float.MIN_VALUE`). `Float.MIN_VALUE` is `1.4E-45` (the smallest positive float), NOT the most negative float. The minimum float value is `-3.4028235E38` = `-Float.MAX_VALUE`.
  - For `getMinValue(Double.class)`, verify the result equals `-Double.MAX_VALUE` (not `Double.MIN_VALUE`). `Double.MIN_VALUE` is `4.9E-324` (the smallest positive double), NOT the most negative double.
  - For `getMaxValue(Float.class)`, verify the result equals `Float.MAX_VALUE`.
  - For `getMaxValue(Double.class)`, verify the result equals `Double.MAX_VALUE`.
  - Use assertion methods like `assertEquals(expected, actual)` with proper constant references (e.g., `assertEquals(-Float.MAX_VALUE, Numbers.getMinValue(Float.class))`).

- Common pitfalls to avoid:
  - ❌ WRONG: Using `Float.MIN_VALUE` as the minimum float value — `Float.MIN_VALUE` is the smallest POSITIVE float (1.4E-45), not the most negative.
  - ❌ WRONG: Using `Double.MIN_VALUE` as the minimum double value — `Double.MIN_VALUE` is the smallest POSITIVE double (4.9E-324), not the most negative.
  - ❌ WRONG: Testing only a subset of numeric types (e.g., only Integer and Long, but not Float and Double).
  - ❌ WRONG: Assuming `Float.MIN_VALUE` equals `Integer.MIN_VALUE` in semantics — they have completely different meanings.

## Examples

### Correct test for getMinValue (will catch the bug):
```java
@Test
public void getMinValue()
{
    assertEquals(Integer.MIN_VALUE, Numbers.getMinValue(Integer.class));
    assertEquals(Integer.MIN_VALUE, Numbers.getMinValue(int.class));
    assertEquals(Long.MIN_VALUE, Numbers.getMinValue(Long.class));
    assertEquals(Long.MIN_VALUE, Numbers.getMinValue(long.class));
    assertEquals(-Float.MAX_VALUE, Numbers.getMinValue(Float.class));  // CORRECT: -3.4028235E38
    assertEquals(-Float.MAX_VALUE, Numbers.getMinValue(float.class));  // CORRECT
    assertEquals(-Double.MAX_VALUE, Numbers.getMinValue(Double.class)); // CORRECT: -1.7976931348623157E308
    assertEquals(-Double.MAX_VALUE, Numbers.getMinValue(double.class)); // CORRECT
    assertEquals(Byte.MIN_VALUE, Numbers.getMinValue(Byte.class));
    assertEquals(Short.MIN_VALUE, Numbers.getMinValue(Short.class));
}
```

### Incorrect test (would NOT catch the bug):
```java
// This incorrect test would pass even with the bug because it uses the wrong constant!
assertEquals(Float.MIN_VALUE, Numbers.getMinValue(Float.class));  // WRONG: Float.MIN_VALUE = 1.4E-45
assertEquals(Double.MIN_VALUE, Numbers.getMinValue(Double.class)); // WRONG: Double.MIN_VALUE = 4.9E-324
```