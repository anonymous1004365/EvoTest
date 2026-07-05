---
name: json-parsing-default-value-numeric-literal
description: When parsing JSON default values for numeric literals, test that both
  integer and decimal (floating-point) values are correctly handled without type conversion
  errors or truncation. Apply when validating default value parsing logic where numeric
  literals may be interpreted as the wrong Java type.
code_tags:
- NULL_CHECK
- VALIDATION
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# json-parsing-default-value-numeric-literal

## Instructions

# JSON Parsing Default Value Numeric Literal Handling

## Instructions

- WHEN the TG encounters a method that parses or converts JSON default value strings (e.g., parsing a column default value expression like `"0"`, `"1.5"`, `"-1"`) into Java types (e.g., `Integer`, `Long`, `BigDecimal`, `String`)
- THEN the TG should **write a parametric test** that exercises the parsing logic with **both integer literals** (e.g., `"0"`, `"1"`, `"-1"`) and **floating-point literals** (e.g., `"1.5"`, `"3.14"`, `"-0.5"`). The test must verify that:
  - A default value string containing an integer (e.g., `"42"`) is correctly parsed to a numeric Java type (e.g., `Long`, `Integer`, `Number`) — not left as a raw `String` when the schema expects a number
  - A default value string containing a decimal (e.g., `"1.5"`) is also correctly parsed to a numeric Java type — and **not** truncated to an integer or thrown away
  - No `NumberFormatException`, `ClassCastException`, or silent type coercion error occurs for either case
- Include **common pitfalls** that the TG might encounter:
  - **Pitfall 1:** Assuming all default value literals are integers. Always test with floating-point values too, since the parser may have a dedicated branch for integer parsing that fails for decimals (e.g., trying `Integer.parseInt()` on `"1.5"`).
  - **Pitfall 2:** Only testing with positive values. Test with zero, positive, and negative values (e.g., `"-1"`, `"0"`, `"1"`).
  - **Pitfall 3:** Not checking the **type** of the parsed result. Even if no exception is thrown, the result could be a `String` instead of a `Number`. Assert that the result is an instance of the expected numeric type.
- **Example of correct test behavior:**
  ```java
  // Parametric test for parseDefaultValue
  @ParameterizedTest
  @CsvSource({
    "0,    0",
    "1,    1",
    "-1,  -1",
    "1.5,  1.5",
    "3.14, 3.14"
  })
  void testParseDefaultValue(String literal, double expected) {
      Object result = parser.parseDefaultValue(literal);
      assertTrue(result instanceof Number, "Result must be a Number, but was " + result.getClass());
      assertEquals(expected, ((Number) result).doubleValue(), 0.0001);
  }
  ```
- **Example of incorrect test behavior (what to avoid):**
  ```java
  // BAD: Only tests integer, doesn't verify type, misses decimal case
  @Test
  void testParseDefaultValue_bad() {
      Object result = parser.parseDefaultValue("0");
      assertEquals("0", String.valueOf(result)); // Wrong: result might be Long(0), and String.valueOf gives "0" anyway
  }
  ```