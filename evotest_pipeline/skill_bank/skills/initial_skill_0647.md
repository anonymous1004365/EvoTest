---
name: template-parameter-type-validation
description: When a template or macro framework supports both String and structured-type parameters, tests must verify that the correct parameter resolution path is used for each type. Named parameters registered under the same key with different types can shadow or conflict with each other, causing type-inappropriate code paths to execute.
code_tags: ['VALIDATION', 'ALTERNATIVE_PROTOCOL_DECODING', 'EXCEPTION_HANDLING']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the code contains a template/macro resolution method that accepts parameters of different Java types (e.g., both `String` and a structured type like `CtTypeReference`, `Map`, `List`, or a custom object) under the **same parameter key name**
- THEN the TG should write a parametric test that:
  1. Registers/defines a parameter with the same key using **both** types (e.g., `template.set("key", "someStringValue")` and `template.set("key", someCtTypeReferenceInstance)`)
  2. Invokes the template/macro resolution that reads parameters by key
  3. **Asserts** that the correct value is resolved for each type path — in particular, that a `String` parameter value is not incorrectly resolved by a code path meant for structured types
  4. Expects the buggy version to return an incorrect value (e.g., a non-null structured-type value when the parameter was actually a String, or vice versa), which manifests as a test failure (wrong output, wrong type, or unexpected `ClassCastException`)
- WHEN there are **separate registration/put methods** for different parameter types (e.g., one for `String` values and one for `CtTypeReference` values)
- THEN the TG must verify that `get(key)` returns the value according to the **correct registration path**, and that the two paths do not collide or shadow each other
- Common pitfalls:
  - Testing only `String` parameters, missing the structured-type parameter collision
  - Assuming that the last-registered value always wins regardless of type
  - Not testing with the **same key** for both types
  - Only testing the happy path and not checking that the type-specific resolution logic picks the right value

## Example (Correct)

```java
// Correct: tests that String parameters are not resolved by the structured-type path
@Test
public void testParameterTypeCollision() {
    Template template = new Template();
    // Register a String parameter
    template.set("myParam", "expectedStringValue");
    // Register a structured-type parameter with the same key
    template.set("myParam", someCtTypeReference);
    
    // The template resolution that reads String parameters should get the String value
    String result = template.evaluateParameter("myParam");
    assertEquals("expectedStringValue", result);
    
    // The template resolution that reads structured-type parameters should get the CtTypeReference
    CtTypeReference refResult = template.evaluateTypeParameter("myParam");
    assertNotNull(refResult);
    assertEquals(someCtTypeReference, refResult);
}
```

## Example (Incorrect — misses the bug)

```java
// Incorrect: only tests String, misses the type collision
@Test
public void testParameterTypeIncomplete() {
    Template template = new Template();
    template.set("myParam", "expectedStringValue");
    
    // This passes even on buggy code, missing the collision bug entirely
    String result = template.evaluateParameter("myParam");
    assertEquals("expectedStringValue", result);
}
```