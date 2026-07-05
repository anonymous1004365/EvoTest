---
name: template-parameter-type-validation
description: This skill teaches how to detect when a method or constructor accepts a template parameter/proxy but fails when passed a non-String type (e.g., CtTypeReference). The TG should trigger this skill when encountering code that accepts Object/raw types for template parameters and processes them conditionally by type.
code_tags: ['NULL_CHECK', 'BOUNDARY_CHECK', 'NPE_CAUSED_BY_MISSING_NULL_CHECK', 'MISSING_TYPE_CHECK']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters code that accepts template parameters (e.g., `Object`, `String`, or raw `Map` values) and processes them by checking their type using `instanceof` or type comparison — especially in contexts like proxy template resolution, template engines, or placeholder replacements — THEN the TG should write a test that passes **multiple types** of template parameter values, including:
  1. A `String` value (the expected/common type)
  2. A non-`String` object such as `CtTypeReference`, `Integer`, or a custom POJO — any type that satisfies a different branch of `instanceof` checks or no explicit branch at all

- WHEN the code processes template parameters by calling methods on them without checking if they are `String` (e.g., calling `contains()`, `replace()`, `toString()` differently based on type), THEN the TG should verify that passing non-String types does NOT cause a `NullPointerException`, `ClassCastException`, or silently produce incorrect output.

- WHEN the code has a condition like `if (val instanceof String)` with an `else` branch that is empty, returns null, or throws, THEN the TG should test both branches: pass both String and non-String values, and verify the behavior is correct (non-null, no exception, expected output).

- Common pitfalls to avoid:
  - ❌ Testing only with `String` type template parameters when the API accepts `Object` — this misses bugs where non-String types cause NPEs or wrong output
  - ❌ Testing only happy path (String values) — always test with at least one non-String type like `CtTypeReference`, `Integer`, or custom object
  - ❌ Assuming `toString()` is always safe — if the code calls `toString()` and then uses the result for string operations (e.g., `contains()`, `matches()`), verify this works for non-String inputs too
  - ❌ Forgetting to verify both the absence of exception AND the correctness of the output/result

### Correct Example

```java
// Good test — tests both String and non-String template parameters
@Test
public void testTemplateParameterWithNonStringType() {
    // Assume we're testing a method like: String resolveTemplate(String template, Map<String, Object> params)
    Map<String, Object> params = new HashMap<>();
    
    // Test with String value (happy path)
    params.put("name", "world");
    String result1 = resolver.resolveTemplate("Hello {{name}}", params);
    assertEquals("Hello world", result1);
    
    // Test with non-String value (e.g., CtTypeReference, Integer, custom object)
    params.put("name", new CtTypeReference<>().setSimpleName("MyClass"));
    String result2 = resolver.resolveTemplate("Hello {{name}}", params);
    // Should not throw NPE — the resolver must handle non-String types safely
    assertNotNull(result2);
    assertTrue(result2.contains("MyClass"));
}
```

### Incorrect Example

```java
// Bad test — only tests String type, misses the bug
@Test
public void testTemplateParameterOnlyString() {
    Map<String, Object> params = new HashMap<>();
    params.put("name", "world");
    // Only testing String — this doesn't catch NPE bugs with non-String values
    String result = resolver.resolveTemplate("Hello {{name}}", params);
    assertEquals("Hello world", result);
}
```