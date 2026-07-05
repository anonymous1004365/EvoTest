---
name: alternative-protocol-decoder-validation
description: When a protocol decoder has alternative decoding paths that handle different
  types (e.g., String templates vs CtTypeReference objects), test all alternative
  paths thoroughly. Missing validation on one path can cause bugs like NullPointerException
  or incorrect behavior.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- VALIDATION
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoder-validation

## Instructions

# Alternative Protocol Decoder Validation

## Instructions

- WHEN the TG encounters a protocol frame decoder or template-based decoder that dispatches to different decoding paths based on parameter type (e.g., one path for String and another for Collection/CtTypeReference objects)
- THEN the TG should write a **parametric test** (using `@ParameterizedTest` or individual test methods) that exercises **each alternative decoding path** separately
- Include test cases for:
  - **String type parameters**: pass plain String values through the decoder
  - **Collection/Object type parameters**: pass non-String type objects (e.g., CtTypeReference, collections, or custom wrapper types) that trigger the alternative branch
- Verify that each path produces the expected output **without** throwing a NullPointerException or returning unexpected null/missing values
- Common pitfalls:
  - Testing only one type of parameter (e.g., only Strings) while the bug exists in the alternative branch
  - Not providing concrete instances for non-String parameters — the test must construct actual CtTypeReference or Collection objects, not nulls
  - Forgetting to assert on the decoded result's content (e.g., verifying that a template parameter retains its expected type and value after decoding)

### Example (correct):
```java
@ParameterizedTest
@ValueSource(strings = {"param1", "param2"})
void testDecodeWithStringType(String value) {
    // When decoder receives a String type, it should encode/decode successfully
    assertDoesNotThrow(() -> decoder.decode(value));
    assertEquals(value, decoder.decode(value));
}
```

### Example (correct):
```java
@Test
void testDecodeWithCtTypeReference() {
    // When decoder receives a CtTypeReference, it should not throw NPE
    CtTypeReference<?> ref = new CtTypeReference<>(String.class);
    Object result = decoder.decode(ref);
    assertNotNull(result);
    assertTrue(result instanceof CtTypeReference);
}
```

### Example (incorrect — only tests one path):
```java
@Test
void testDecodeOnlyString() {
    // Missing test for the CtTypeReference path where the bug exists
    assertEquals("hello", decoder.decode("hello"));
}
```