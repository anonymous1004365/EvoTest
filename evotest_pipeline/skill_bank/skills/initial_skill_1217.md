---
name: template-proxy-decoding-validation
description: When testing a protocol decoder that supports multiple template types
  for proxy configuration, the TG should verify that both types work correctly by
  testing all template parameter types, not just one.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- ARGUMENT_VALIDATION
test_pattern: PARAMETRIC_TEST
---

# template-proxy-decoding-validation

## Instructions

# Template Proxy Decoding Validation

## Instructions

- WHEN the TG encounters a protocol decoder that uses typed templates for proxy configuration (e.g., `Template<String>` and `Template<CtTypeReference>`) to parse alternative protocol data from different device types
- THEN the TG should create a parametric test (e.g., `@ParameterizedTest` with `@ValueSource` or `@MethodSource`) that tests decoding for each supported template parameter type
  - For example, if the decoder supports both `Template<String>` and `Template<CtTypeReference>`, write a test case for each type
  - Include at least one valid input for each type variant
  - Verify that the decoder correctly parses the message without throwing an exception and returns the expected decoded object
- Common pitfalls:
  - Testing the decoder with only one template type (e.g., only `String` or only a single device type), which misses the bug in the second type
  - Assuming one type variant is sufficient to cover all cases — a fix applied to only one template type may break the other
  - Not checking that the decoded result is non-null or has the expected structure for each type variant
  - Not using a parameterized test approach, leading to duplicated or missing test cases

### Correct Example (Parametric Test)

```java
@ParameterizedTest
@ValueSource(strings = {
    "stringTemplateInput",
    "ctTypeReferenceTemplateInput"
})
void testDecodeWithTemplateTypes(String input) {
    GatorProtocolDecoder decoder = new GatorProtocolDecoder();
    Object result = decoder.decode(null, null, input);
    assertNotNull(result);
    // further assertions on result structure
}
```

### Incorrect Example (Only One Type)

```java
@Test
void testDecodeWithStringTemplate() {
    GatorProtocolDecoder decoder = new GatorProtocolDecoder();
    Object result = decoder.decode(null, null, "stringTemplateInput");
    assertNotNull(result);
}
// Missing test for CtTypeReference template — the bug for that type goes undetected
```