---
name: proxy-template-decoder-type-validation
description: When a proxy/template decoder uses placeholder substitution (e.g., {param})
  to extract parameters from protocol messages, test that the decoder correctly resolves
  both String and non-String (e.g., CtTypeReference) types when extracting parameter
  values, not just the common String case.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# proxy-template-decoder-type-validation

## Instructions

# Proxy Template Decoder: Non-String Parameter Type Resolution

## Instructions

- WHEN the TG encounters a protocol decoder that uses a template/pattern mechanism with placeholder keys (e.g., `{param}`) to extract parameters from messages, and the decoder resolves these placeholders by looking up values from a parameter map
- THEN the TG should test that when the decoder processes template placeholders, it correctly handles parameter values that are **non-String types** (e.g., `CtTypeReference`, custom objects) — not just String type parameters
- Specifically, the TG should verify that the `toString()` method or explicit String conversion is called on non-String parameter values when they are substituted into the template pattern, and that the resulting string substitution produces the expected output
- Include a test case where a parameter value is set to a non-String object (such as `CtTypeReference` with a class name like `"java.util.List"`), and verify that the decoded/rendered output contains the expected string representation of that object
- Common pitfalls to avoid:
  - Testing only with String type parameter values, which would pass even if the decoder silently skips or mishandles non-String types
  - Assuming that non-String parameter values are always cast to String before substitution
  - Not verifying that the final decoded output (e.g., the rendered message after parameter substitution) matches expectations; instead, only checking intermediate states

### Example (correct approach):
```java
// Given a decoder that substitutes {param} placeholders in a template string
// using values from a parameter map, verify that non-String values are correctly rendered:

Properties properties = new Properties();
properties.setProperty("generic", "java.util.List");
CtTypeReference type = new CtTypeReference("java.util.List");
templateDecoder.registerParameter("type", type);

String result = templateDecoder.decode("The type is {type}");
assertEquals("The type is java.util.List", result);
```

### Example (incorrect approach):
```java
// BAD: Only testing with String parameter values - won't catch the bug
Properties properties = new Properties();
templateDecoder.registerParameter("type", "java.util.List"); // String, not CtTypeReference

String result = templateDecoder.decode("The type is {type}");
assertEquals("The type is java.util.List", result);
// This passes but does NOT test that the decoder handles non-String values
```

### What to verify on the buggy version:
- When a non-String type (e.g., `CtTypeReference`) is passed as a parameter value to a template decoder that swaps placeholders using string substitution, the buggy version may produce an incorrect output (e.g., `"The type is java.util.List[]"` instead of `"The type is java.util.List"`) or may throw an unexpected exception
- The fixed version should properly call `toString()` or apply explicit String conversion, producing the expected output without extraneous characters