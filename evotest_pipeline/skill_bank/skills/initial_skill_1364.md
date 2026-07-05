---
name: template-parameter-type-validation
description: >
code_tags: ['ARGUMENT_VALIDATION', 'STATE_MUTATION', 'TYPE_CONVERSION', 'TEMPLATE_PARAMETER_TYPE_VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that accepts template parameters as either `String` or a wrapper/reference type (e.g., `CtTypeReference`, `TemplateParameterModel`, `Class`, `Object`) in the same parameter position, and the method serializes or delegates one type to a different internal path than the other
  - THEN the TG must write multiple test cases: one using a `String` parameter and another using the **non-String** type parameter (e.g., a mock or stub `CtTypeReference`, a fake `TemplateParameterModel`)
  - The test must verify that the non-String type does NOT cause a `NullPointerException` when processed
  - The test must verify that the non-String type produces the correct serialized output, not just that it "does not crash"
- WHEN the TG sees a method that converts template parameter types (e.g., calling `.toString()` on an assumed-String parameter, or calling methods only available on one type without an `instanceof` guard)
  - THEN the TG must check all branches of any `if (x instanceof String)` / `if (x instanceof CtTypeReference)` conditional
  - The test must assert the correct output for EACH branch
- Common pitfalls to avoid:
  - Testing only the `String` type parameter and assuming all other types work the same way
  - Verifying only that "no exception is thrown" without asserting the correct expected serialized output
  - Forgetting that mock/stub implementations may differ from real implementations — prefer real instances when possible

**Example (correct):**
```java
// Given a method that handles both String and CtTypeReference parameter types:
// TemplateProxyFactory.serializeMethodParam(Object param)

// Test with String parameter:
Object result1 = proxyFactory.serializeMethodParam("hello");
assertEquals("\"hello\"", result1);

// Test with CtTypeReference parameter (triggers the NullPointerException bug):
CtTypeReference<?> ref = new CtTypeReference<>() {{
    setSimpleName("java.util.List");
}};
// Without the fix, this would throw NPE
Object result2 = proxyFactory.serializeMethodParam(ref);
assertEquals("\"java.util.List\"", result2);
```

**Example (incorrect):**
```java
// Only testing String path — misses the bug!
assertEquals("\"hello\"", proxyFactory.serializeMethodParam("hello"));

// Or: testing non-String path but only checking "no exception":
assertDoesNotThrow(() -> proxyFactory.serializeMethodParam(mockRef));
// This passes even if the output is null or wrong! Must verify the actual output.
```