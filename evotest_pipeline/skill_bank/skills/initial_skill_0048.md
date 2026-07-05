---
name: template-parameter-type-validation
description: When processing proxy template parameters, the TG should test with both String and non-String CtTypeReference types to ensure equals() and validation logic handle type hierarchy correctly. This skill applies when template parameter types are validated against a non-generic proxy interface.
code_tags: ['TYPE_REFERENCE_EQUALS', 'INHERITANCE_CHECK', 'VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters code that validates or compares template/proxy parameter types against a non-generic interface (e.g., `CtTypeReference` comparison using `equals()` against a hardcoded type like `String`), the test should verify behavior with **both the exact type and subclasses/subtypes**.
- WHEN a method filters or processes parameters based on whether they match a specific `CtTypeReference` type, THEN the TG should test with at least two parameter type categories:
  1. Parameters whose type is exactly the expected `CtTypeReference` (e.g., `String`)
  2. Parameters whose type is a **different `CtTypeReference`** (e.g., `Integer`, `Boolean`, or a custom class type)
- WHEN `CtTypeReference.equals()` is involved in a decision (e.g., checking `param.getType().equals(someTypeRef)`), THEN the test should verify that the behavior **differs** for matching vs non-matching types, and that the code does NOT accidentally match or reject a type that is semantically distinct (e.g., a generic `CtTypeReference` wrapping `Integer` vs `String`).
- **Common pitfall**: Testing only with `String` type parameters, missing that the code may incorrectly classify or reject non-String parameters due to flawed `equals()` logic or type hierarchy assumptions.
- **Common pitfall**: Assuming `CtTypeReference.equals()` behaves like standard Java `Class.equals()` — it may not account for type inheritance or may fail on parameterized types.
- The test should expect that **buggy code processes or validates non-matching types incorrectly** (e.g., fails to reject them, or throws an unexpected exception), while **fixed code handles them correctly** (e.g., returns `false` for mismatched types, or correctly delegates to subclass behavior).

### Correct example:
```java
// Test with BOTH String type AND Integer type parameters
@Test
public void testTemplateParameterTypeValidation() {
    // Given: a processor that only accepts String-type parameters
    TemplateParameterProcessor processor = new TemplateParameterProcessor();
    
    // When: parameter type matches String
    CtTypeReference stringType = factory.Type().stringType();
    CtParameter<?> stringParam = createParameter(stringType, "name");
    boolean resultForString = processor.accept(stringParam);
    assertTrue("Should accept String type", resultForString);
    
    // When: parameter type does NOT match String (e.g., Integer)
    CtTypeReference integerType = factory.Type().integerType();
    CtParameter<?> integerParam = createParameter(integerType, "count");
    boolean resultForInteger = processor.accept(integerParam);
    assertFalse("Should reject non-String type", resultForInteger);
}
```

### Incorrect example:
```java
// BAD: only tests with String - misses the bug
@Test
public void testOnlyStringType() {
    TemplateParameterProcessor processor = new TemplateParameterProcessor();
    CtTypeReference stringType = factory.Type().stringType();
    CtParameter<?> stringParam = createParameter(stringType, "name");
    assertTrue("Should accept String type", processor.accept(stringParam));
    // Does not test Integer, Boolean, or custom types
}
```