---
name: template-parameter-type-validation
description: When a method accepts template parameters (generic/parametric types), the TG should verify that it correctly handles both Class-type and String-type inputs. This skill catches bugs where parameter type validation is too narrow.
code_tags: ['ORDER_DEPENDENCY', 'STATE_MUTATION', 'VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that takes a template parameter (e.g., a `String param` that represents a type name, or a `Class<?>` parameter used for type resolution)
- THEN it should write a parametric test that exercises the method with BOTH:
  1. A **Class-type parameter**: pass an existing class literal (e.g., `String.class`, `Integer.class`)
  2. A **String-type parameter**: pass a fully qualified class name as a String (e.g., `"java.lang.String"`, `"spoon.Launcher"`)
- The test should verify that the method produces the same result for semantically equivalent inputs of different types. Specifically:
  - If the method processes parameters by iterating over them (e.g., using `forEach` or a for loop), verify that ALL parameters are correctly processed, not just the first or last one
  - If the method checks instance types (e.g., `instanceof` checks on elements), ensure that both `CtTypeReference` objects and `String` objects are handled
- **Common pitfalls to avoid**:
  - ❌ Testing with only one type of parameter (e.g., only `String` or only `Class`)
  - ❌ Assuming that because the method signature accepts `Object`, it handles all input types interchangeably
  - ❌ Only testing with a single parameter — test with MULTIPLE parameters of mixed types
  - ❌ Not verifying the error/exception behavior: some methods may throw exceptions for one parameter type and silently succeed for another, which is a bug
- **Correct approach example**:
```java
@Test
public void testMixedTemplateParameterTypes() {
    // Setup: create the object under test
    SomeTemplateProcessor processor = new SomeTemplateProcessor();
    
    // Test with Class-type and String-type mixed
    processor.setTemplateParameters("java.lang.String", Integer.class);
    
    // Verify all parameters were correctly processed
    List<CtTypeReference<?>> refs = processor.getTemplateTypeReferences();
    assertEquals(2, refs.size());
    // Both should resolve to proper type references
}
```
- **Incorrect approach example**:
```java
@Test
public void testTemplateParameters_OnlyString() {
    // BUG: Only testing String type, missing Class type handling
    SomeTemplateProcessor processor = new SomeTemplateProcessor();
    processor.setTemplateParameters("java.lang.String", "java.lang.Integer");
    // This passes for String-only inputs but would miss Class-type bugs
}
```