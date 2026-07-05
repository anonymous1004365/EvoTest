---
name: template-parameter-type-validation
description: When a protocol decoder or generic data processor uses a shared template/pattern with mixed parameter types (e.g., String and CtTypeReference), tests should verify both type branches to ensure correct parameter extraction and avoid unexpected type errors.
code_tags: ['ALTERNATIVE_PROTOCOL_DECODING']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the code contains a `template` or pattern-based parameter extraction mechanism where parameters can be of different types (e.g., `String` and `CtTypeReference`), and the code uses `instanceof` checks or type-specific handling to extract parameter values
- THEN the TG should write tests that exercise **all** known type branches of the parameter extraction logic, not just the most obvious or common type
- Specifically, test with parameters of each supported type (e.g., `String` for the simple case, `CtTypeReference` for the complex/jar-analysis case), and verify that the extracted parameter value is correct for each type
- The test should also verify that the method correctly handles situations where certain parameter types might be unexpectedly passed, ensuring that type-based dispatch does not silently skip or corrupt parameters of a less common type
- **Common pitfalls:**
  - Testing only one parameter type (e.g., only `String` values) while the logic handles multiple types with different branches
  - Assuming the template parameter list is homogeneous when it can contain mixed types
  - Not verifying that type-specific `instanceof` branches map to the correct parameter positions/indexes

### Correct (Recommended) Test Pattern

```java
// Test with multiple parameter types to exercise all branches
public void testDecodeWithMixedParameterTypes() {
    // Create template with parameters of different types
    Template template = new Template("...");
    template.addParameter("param1", "stringValue");
    template.addParameter("param2", new CtTypeReference(String.class));
    
    // Execute decoding
    Result result = decoder.decode(template);
    
    // Verify each parameter type branch produced correct output
    assertEquals("stringValue", result.getParameter(0));
    assertEquals(String.class, result.getParameterAsType(1));
}
```

### Incorrect (Bug-Prone) Pattern

```java
public void testDecodeWithStringOnly() {
    // Only tests String type parameters — misses CtTypeReference branch
    Template template = new Template("...");
    template.addParameter("param1", "stringValue");
    template.addParameter("param2", "anotherString");
    
    Result result = decoder.decode(template);
    // If the second parameter was meant to be a CtTypeReference,
    // this test won't catch the bug
}
```