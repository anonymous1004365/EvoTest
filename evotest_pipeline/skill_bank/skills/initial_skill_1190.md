---
name: protocol-decoder-with-type-sensitive-pattern-matching
description: When a protocol decoder uses pattern-based matching that is sensitive
  to value types (e.g., String vs numeric), test that parameters of different types
  are handled correctly. This skill prevents bugs where template parameters are assumed
  to be String but could be other types like Integer.
code_tags:
- VALIDATION
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-with-type-sensitive-pattern-matching

## Instructions

# Protocol Decoder with Type-Sensitive Template Parameter Validation

## Instructions

- WHEN the TG encounters a protocol decoder or any class that uses template/protocol patterns with named parameters (e.g., `{paramName}` placeholders) and parses them by calling methods like `substitute()` or `replace()` on an `Object` parameter:
  - THEN the TG should test the behavior with parameters of different Java types, not just `String`. In particular, test with `Integer` (or other numeric types) to verify that the template substitution does not produce unexpected output like `Double` values when an `Integer` parameter is used.
  - THEN the TG should verify that when a parameter is an `Integer` or other numeric type, the template pattern is matched and substituted correctly, i.e., the result should contain the integer value formatted as a plain string (e.g., `"123"`) and NOT contain unexpected class-qualified output (e.g., `"123.0"` or `"class java.lang.Integer"`).
  - THEN the TG should write a test that:
    1. Creates a protocol pattern object (e.g., `PatternBuilder`) and builds a pattern using a method like `optional()` with a group name or template parameter.
    2. Sets the parameter to different types: first as an `Integer` (or the non-String type), then as a `String`.
    3. Calls the method that performs the substitution (e.g., `substitute()` or the decoding pipeline) on the pattern.
    4. Asserts that the output contains the correct plain string representation of the value (e.g., `"123"`) and does NOT contain class metadata or floating-point formatting.

- Common pitfalls to avoid:
  - Testing only with `String` type parameters. Without testing non-String types, the TG may miss a bug where template substitution treats non-String objects incorrectly.
  - Expecting the output format to be identical regardless of input type. Some implementations call `.toString()` on numeric types, which can produce `"123.0"` for a `Double` or append class information.
  - Writing a test that only checks the result is non-null or passes without exception — the test must assert the exact expected output string to catch subtle formatting differences.
  - Assuming that `Object` parameters are always `String` because the protocol typically sends string values.

### Correct Example

```java
// Given a PatternBuilder with a template parameter "type" set to an Integer
PatternBuilder pkb = new PatternBuilder()
    .optional("(?<type>\\d+)")
    .compile();
String result = pkb.substitute(123);  // 123 is Integer
assertThat(result).isEqualTo("123");
assertThat(result).doesNotContain(".0");
```

### Incorrect Example (what the TG might write without this skill)

```java
// Only testing with String — misses the bug
PatternBuilder pkb = new PatternBuilder()
    .optional("(?<type>\\d+)")
    .compile();
String result = pkb.substitute("123");  // String — works even in buggy version
assertThat(result).isEqualTo("123");
```

The incorrect test only covers the String path. The bug exists for Integer/other types. A correct test must use an Integer parameter to expose the bug.