---
name: type-code-separator-enforcement
description: This skill teaches how to test TypeCodes that use separator characters
  for encoding/decoding. When a type-code separator character is used to delimit type
  prefix from the value, tests must verify both encode and decode with values that
  contain or lack the separator.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# type-code-separator-enforcement

## Instructions

# Type Code Separator Enforcement

## Instructions

- WHEN the TG encounters a utility class like `TypeCodes` that implements `encode(type, value)` and `decode(data)` methods using a fixed separator character (e.g., `':'` colon, `'.'` period) to delimit a type prefix from a value
- THEN the TG MUST write a parametric test that exercises both `encode()` and `decode()` in tandem, verifying round-trip consistency across a variety of value strings, including:
  1. Values that DO NOT contain the separator character (e.g., `"blobId"`, `"hello"`)
  2. Values that CONTAIN the separator character (e.g., `"bin:2342"`, `"ns:localname"`, `"prefix:value:more"`)
  3. Edge cases such as empty string `""`, values starting/ending with separator (e.g., `":start"`, `"end:"`), and values consisting solely of the separator (`":"`)
- The test MUST assert that `decode(encode(type, value))` returns the original value exactly for all cases, and that the decoded type prefix equals the original type
- Common pitfalls:
  - **Testing only one type of value** — e.g., testing only values without the separator and assuming all values behave the same
  - **Forgetting to test both encode and decode** — if only encode is tested, a corrupted encoding that happens to pass a single test case won't be caught
  - **Using magic strings as expected values** — hardcoding expected encoded strings masks the round-trip invariant that `decode(encode(x)) == x`

### Correct example (JUnit 5 parameterized test):

```java
@ParameterizedTest
@CsvSource({
    "blobId",
    "bin:2342",
    "ns:localname",
    ":start",
    "end:",
    ":",
    "",
    "simple",
    "a:b:c:d"
})
void testEncodeDecodeRoundTrip(String value) {
    String type = "bin";
    String encoded = TypeCodes.encode(type, value);
    // For values without ':', encoded = "bin:value"
    // For values with ':', encoded type must remain "bin" and encoded must contain original value
    Decoded decoded = TypeCodes.decode(encoded);
    assertEquals(type, decoded.type);
    assertEquals(value, decoded.value);
}
```

### Incorrect example (does not catch the bug):

```java
@Test
void testEncode() {
    // Only tests value without separator — misses logic errors with embedded separators
    String encoded = TypeCodes.encode("bin", "blobId");
    assertEquals("bin:blobId", encoded);
}
```