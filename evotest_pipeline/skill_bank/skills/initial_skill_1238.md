---
name: protocol-alternative-decoding-path-validation
description: ''
code_tags:
- VALIDATION
- TYPE_CONVERSION
- EXCEPTION_HANDLING
test_pattern: PARAMETRIC_TEST
---

# protocol-alternative-decoding-path-validation

## Instructions

# Protocol Alternative Decoding Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder that can accept **multiple alternative parameter types** (e.g., `String` vs `byte[]`, or different data formats), or that processes data through **multiple conditional branches** (e.g., checking protocol version, data source, or format indicator):
  - THEN the TG should write **parametric tests that exercise each alternative path** with both valid and **malformed/edge-case inputs**.
  - For each test case, verify the decoder produces the expected output for valid inputs **and** throws a meaningful exception (not a generic `NullPointerException` or `ClassCastException`) for malformed inputs.
  - Specifically, include test cases where:
    1. The input is completely empty/missing (e.g., empty `String`, empty `byte[]`)
    2. The input has an unexpected format (e.g., wrong delimiter, missing fields, truncated data)
    3. The input triggers a TYPE_CONVERSION issue (e.g., attempting to treat a non-numeric string as a number, or vice versa)
  - Assert that the decoder does NOT throw an `ArrayIndexOutOfBoundsException`, `NullPointerException`, or other unhandled runtime exception — it should throw a custom, domain-specific exception or return a sensible fallback value.
  - **Common pitfalls to avoid:**
    - ❌ Testing only the "happy path" (most common format) and ignoring alternative decoding branches
    - ❌ Catching generic `Exception` and swallowing it, leaving no trace of the error
    - ❌ Assuming the same input format is always used across all devices/protocol versions
    - ❌ Not testing with `null` or empty values when the decoder may receive them from network buffers

- **Correct example (conceptual):**
```java
@ParameterizedTest
@CsvSource({
  "validPayload,expectedPosition",
  "'', ''",       // empty payload
  "nullPayload",  // null from some source
  "garbageData"   // malformed
})
public void testDecodeMultipleFormats(String input, String expected) {
    if (expected == null || expected.isEmpty()) {
        assertThrows(ProtocolDecodeException.class, () -> decoder.decode(input));
    } else {
        assertEquals(expected, decoder.decode(input));
    }
}
```

- **Incorrect example (conceptual):**
```java
// Only tests one format path — misses alternative branch entirely
@Test
public void testDecode() {
    assertEquals(expected, decoder.decode("valid_data_with_expected_format"));
}
```