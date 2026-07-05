---
name: template-parameter-type-validation
description: When writing tests for code templates with typed parameters (e.g., String, CtTypeReference), test each parameter type individually to ensure the template engine correctly handles all types. This skill catches cases where one parameter type overwrites or shadows another during template evaluation.
code_tags: ['NULL_CHECK', 'VALIDATION', 'BOUNDARY_CHECK']
test_pattern: STATE_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Binding Validation

## Instructions

- WHEN the TG encounters a code template that accepts parameters of different Java types (e.g., a template method taking both `String` value parameters and `CtTypeReference` type parameters)
- THEN it should write a test that exercises each parameter type independently, verifying that the template engine correctly resolves and applies each parameter without interference or type-confusion
- Specifically: include test data where:
  - A `String` parameter has a simple string value
  - A `CtTypeReference` parameter (or other non-String type) has a type reference value
  - Verify the resulting template output contains the expected content for EACH parameter type, not just one
- Common pitfalls to avoid:
  - Testing only `String` type parameters while ignoring `CtTypeReference` or other non-primitive types
  - Assuming the template engine treats all parameter types identically
  - Writing a test that passes because the correct output occurs only by coincidence (e.g., one parameter accidentally producing the expected output for another)
  - Not checking the **combined** output: verify that the result contains ALL expected elements from ALL parameter types

### Example (Correct):
```java
// Given a template with parameters: paramName (String), paramType (CtTypeReference)
// Expected output: the field name comes from paramName, the type comes from paramType
SomeTemplate t = new SomeTemplate();
t.paramName = "myField";
t.paramType = factory.Type().stringType();
CtField<?> result = t.apply();
assertEquals("myField", result.getSimpleName());
assertEquals("String", result.getType().getSimpleName());
```

### Example (Incorrect — will miss the bug):
```java
// BUG: Only tests String parameter, never exercises CtTypeReference
SomeTemplate t = new SomeTemplate();
t.paramName = "myField";
CtField<?> result = t.apply(); 
// Test passes by coincidence but masks the bug where CtTypeReference handling is broken
```

### Example (Incorrect — wrong assertion):
```java
// BUG: Asserts the field name but doesn't verify the type came from the CtTypeReference
SomeTemplate t = new SomeTemplate();
t.paramName = "myField";
t.paramType = factory.Type().stringType();
CtField<?> result = t.apply();
assertEquals("myField", result.getSimpleName()); // Okay
assertEquals("myField", result.getType().getSimpleName()); // Wrong! Should be "String", not "myField"
```