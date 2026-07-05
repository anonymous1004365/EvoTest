---
name: template-proxy-type-validation
description: When validating proxy template parameters, test that both CtTypeReference (class) and String types are correctly handled as template parameter types, not just String. This prevents ClassCastException when a type reference is mistakenly treated as a String.
code_tags: ['BOUNDARY_CHECK', 'STATE_MUTATION', 'VALIDATION', 'INHERITANCE_CHECK', 'TYPE_HIERARCHY_CHECK']
test_pattern: EXCEPTION_TEST
---

# template-proxy-type-validation

## Instructions

# Template Proxy Type Validation

## Instructions

- WHEN the TG encounters a method that validates or processes proxy template parameters (e.g., a `TemplateProxy` constructor, `validateProxy`, or similar), and the code checks parameter types using `instanceof` or `getClass()` comparisons with `String` type
- THEN the TG should write a test that passes a non-String type (such as a `CtTypeReference` or its wrapper) as a template parameter, to verify the code correctly handles non-String typed parameters without throwing a `ClassCastException` or `IllegalArgumentException` related to type mismatches
- Include concrete examples: use e.g. `CtTypeReference<?>` objects obtained via `factory.Type().get(...)` or `CtClass.toReference()` to represent class-level types
- Verify that the code correctly delegates or validates for both `String` and `CtTypeReference` parameter types, e.g., that `CtTypeReference` parameters are not cast to `String` directly
- Common pitfalls: testing only `String` type parameters, assuming all template parameters are strings, or forgetting to test with the actual wrapper/type-reference objects that the code uses internally
- The test should assert that no exception is thrown (or a specific expected exception occurs) when a non-String type is passed as a template parameter, and that the resulting proxy object behaves correctly

### Correct test example:
```java
// Test that CtTypeReference works as a template parameter type
@Test
public void testTemplateWithTypeReference() {
    CtTypeReference<?> ref = factory.Type().get(String.class);
    Object templateParam = ref; // or wrap as appropriate
    // Should not throw ClassCastException
    TemplateProxy proxy = new TemplateProxy(templateParam);
    assertNotNull(proxy);
    assertEquals(ref, proxy.getValue());
}
```

### Incorrect test example (missing type coverage):
```java
// BUG: Only tests String type, missing the non-String case
@Test
public void testTemplateWithString() {
    TemplateProxy proxy = new TemplateProxy("myParam");
    assertNotNull(proxy);
    // Does not test CtTypeReference at all
}
```