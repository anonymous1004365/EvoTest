---
name: template-parameter-type-validation
description: When validating or adding parameters to proxy templates, test with both String and non-String (e.g., CtTypeReference) types to ensure type-based validation logic handles non-String arguments correctly and doesn't skip essential parameter filtering.
code_tags: ['ARGUMENT_VALIDATION', 'NULL_CHECK', 'BOUNDARY_CHECK', 'STATE_MUTATION', 'TYPE_CONVERSION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters code that validates, adds, or processes parameters in a template or proxy template context (e.g., methods like `addOrUpdateParameter`, `addParameter`, or parameter validation logic that checks parameter types)
- THEN the TG should write a parameterized test that passes parameters of different Java types — specifically BOTH `String` values and non-String type references (e.g., `CtTypeReference` objects) — and verify that:
  1. Parameters of type `String` are accepted/processed correctly
  2. Parameters of type `CtTypeReference` (or other non-String types) are also accepted/processed without throwing exceptions or being silently skipped
  3. The template's internal state (e.g., parameter count, parameter list) correctly reflects all added parameters regardless of their type
- Common pitfalls to avoid:
  - Testing only with `String` type parameters, which may cause the TG to miss bugs where the code uses `instanceof String` or similar type checks to make decisions about whether to process a parameter
  - Assuming that because a method accepts `Object` as a parameter type, all object types are treated equally
  - Not verifying the side effects or state after adding parameters of different types

### Correct Example:
```java
// Tests that both String and CtTypeReference parameters are accepted
@Test
public void testAddOrUpdateParameterWithDifferentTypes() {
    // Create a template with a CtTypeReference parameter
    CtTypeReference<?> typeRef = factory.Type().createReference("java.util.List");
    template.addOrUpdateParameter("listType", typeRef);
    
    // Create a template with a String parameter
    template.addOrUpdateParameter("name", "hello");
    
    // Verify both parameters are present
    assertEquals(2, template.getParameters().size());
}
```

### Incorrect Example:
```java
// Only tests String parameters - misses the bug
@Test
public void testAddOrUpdateParameter() {
    template.addOrUpdateParameter("name", "hello");
    assertEquals(1, template.getParameters().size());
}
```