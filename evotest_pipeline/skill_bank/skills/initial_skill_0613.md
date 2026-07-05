---
name: template-parameter-type-validation
description: Use when testing template processing that validates parameter types — ensure the method correctly rejects unsupported parameter types (like objects) while accepting supported ones (like strings, CtTypeReference).
code_tags: ['VALIDATION']
test_pattern: EXCEPTION_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters methods that validate template parameters (e.g., checking if a parameter is a `String`, `CtTypeReference`, or other supported type for template processing)
- THEN the TG should test with at least one **unsupported type** (e.g., a generic `Object`) as a parameter value, and verify that the method throws an appropriate exception (e.g., `TemplateException`) when encountering that unsupported type
- WHEN the TG sees template validation that accepts `String` and `CtTypeReference` types as template parameters, THEN the TG should test with **both** a valid `String` parameter and a valid `CtTypeReference` parameter to confirm they are accepted, AND test with an **invalid `Object` parameter** to confirm it is rejected
- Common pitfall: The TG might test only with valid parameter types (e.g., only `String`, only `CtTypeReference`, or only the type mentioned in the focal method) and miss the bug entirely. The TG MUST also test with an unsupported type like `Object` to ensure the validation logic correctly rejects it.
- The exception should match what the buggy code would throw — typically the method throws something like a `TemplateException` or similar runtime exception when validation fails.
- Include: (1) a valid case that should pass, (2) an invalid case with an unsupported parameter type that should trigger the exception.

```java
// CORRECT test approach: test both valid and invalid parameter types
@Test
public void testTemplateParameterTypeValidation() {
    // Setup template and context
    Template template = ...;
    TemplateContext context = ...;

    // Valid case: String parameter
    context.addParameter("key1", "stringValue"); // should be accepted
    template.process(context); // should not throw

    // Invalid case: Object parameter
    context.addParameter("key2", new Object()); // should be rejected
    assertThrows(TemplateException.class, () -> template.process(context));
}
```

```java
// INCORRECT test approach: only testing valid parameters
@Test
public void testTemplateParameterTypeValidation() {
    Template template = ...;
    TemplateContext context = ...;
    context.addParameter("key", "stringValue");
    template.process(context);
    // Bug not caught — Object parameter type is never tested
}
```