---
name: template-parameter-type-validation
description: When a protocol decoder or similar class reads template parameters from a string list and processes them into typed objects, it must handle mixed types (e.g., String and numeric) correctly without missing parameters. Use this skill to write tests that verify all parameter types are processed and returned.
code_tags: ['VALIDATION', 'TYPE_CONVERSION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a protocol decoder that parses a template parameters string (e.g., a comma-separated list of position data fields like `"$GPRMC,207069,0,0,0,,,A"`) and converts each segment into typed objects (e.g., `String`, `Integer`, `Double`, `Long` for different data types like device ID, speed, course, satellites, etc.)
- THEN it should test that ALL parameter types present in the template are correctly returned when the decoder processes the string. In particular, it must verify that when the template contains both `String`-type parameters (e.g., device serial/firmware) AND `CtTypeReference`-type parameters (e.g., object references), the decoder processes every segment and does not skip or drop any portion.
- Include a concrete test case with a template that mixes `String` and `CtTypeReference`-like typed parameters (e.g., using an actual device ID string like `"207069"` followed by numeric/object parameters), and verify that the decoded result contains the expected number of parameters with correct types — e.g., the first parameter should be a `String` equal to the device ID, not null or missing.
- A common pitfall is to test only with all-`String`-type parameters or only all-numeric parameters, which masks bugs where mixed-type templates cause the parser to miscalculate positions or skip segments. Always include a mixed-type test case.
- Another common pitfall is to assume that if the first parameter is processed correctly, the rest will be too. Test the full output length and each parameter's value individually.

### Correct Example

```java
// Mixed types: String device ID, then various numeric/object types
@Test
public void testDecodeWithMixedParameterTypes() {
    TrvProtocolDecoder decoder = new TrvProtocolDecoder();
    // Template: String, int, int, int, (skipped), String
    String testData = "$GPRMC,207069,0,0,0,,,A";
    // ... decode and verify length == 6, param[0] == "207069", param[4] == null or empty string, etc.
}
```

### Incorrect Example

```java
// INCORRECT: Only tests with data where all parameters are String type
@Test
public void testDecodeAllStrings() {
    TrvProtocolDecoder decoder = new TrvProtocolDecoder();
    String testData = "abc,def,ghi";
    // This misses the bug that only appears when types are mixed
}
```