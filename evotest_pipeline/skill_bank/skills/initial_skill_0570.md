---
name: template-parameter-type-validation
description: When validating proxy template parameters that can be either a String or a typed reference, test with all valid types including CtTypeReference to ensure type-specific validation logic works correctly and does not throw unexpected exceptions.
code_tags: ['ARGUMENT_VALIDATION', 'TYPE_CONVERSION', 'STATE_MUTATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that validates or processes template/proxy parameters where the input can be of multiple types (e.g., String, CtTypeReference), and the method uses `instanceof` checks to branch validation logic
- THEN the TG should write a test that exercises the validation with each distinct input type, especially:
  - Test with a plain String value as a parameter
  - Test with a CtTypeReference (or other typed reference object) as a parameter
  - Verify that neither case throws a ClassCastException, NullPointerException, or unexpected validation failure
  - For the typed reference case, verify the validation correctly extracts and processes the underlying type information
- Include concrete values: use actual CtTypeReference instances (e.g., from `factory.Type().get(CoreTemplate.class)`), not just mocks
- Common pitfalls:
  - Testing only String-type parameters and assuming other types work the same way
  - Not creating a real CtTypeReference instance to exercise the `instanceof` branch
  - Forgetting that `instanceof` checks might fail on certain subtypes or wrapped objects
  - Not verifying that the method returns the expected validation result for each type

Examples:

❌ Incorrect (tests only String type):
```java
@Test
public void testValidateTemplateParameter() {
    // Only tests String - misses the CtTypeReference branch
    processor.addParameter("key", "someString");
    processor.validate(); // works fine
}
```

✅ Correct (tests all parameter types):
```java
@Test
public void testValidateTemplateParameterWithString() {
    processor.addParameter("name", "myTemplate");
    processor.validate();
    // expected: no exception, parameter accepted
}

@Test
public void testValidateTemplateParameterWithCtTypeReference() {
    CtTypeReference<?> typeRef = factory.Type().get(CoreTemplate.class);
    processor.addParameter("type", typeRef);
    processor.validate();
    // expected: no ClassCastException, parameter accepted with type info
}
```