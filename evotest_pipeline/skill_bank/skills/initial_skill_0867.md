---
name: proxy-type-parameter-validation
description: When code processes proxy template parameters accepting Object types
  and uses them as a replaced element, test that both CtTypeReference and String type
  parameters are handled correctly without causing a ClassCastException.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- ARGUMENT_VALIDATION
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# proxy-type-parameter-validation

## Instructions

# Proxy Type Parameter Validation

## Instructions

- WHEN the TG encounters code that processes proxy/interceptor template parameters (e.g., parameters like `$class$`, `$proceed$`) where the parameter type is `Object` and the value is later used as a specific type (e.g., as a `CtTypeReference` or `String`)
- THEN the TG should write a parameterized test that passes each valid type of parameter value through the processing logic:
  - Test with a `CtTypeReference` type parameter value
  - Test with a `String` type parameter value  
  - Test with any other valid type the parameter could accept
  - Verify that ALL accepted types are processed without throwing a `ClassCastException`
- Include concrete values: For a proxy template that accepts parameters like `$class$` (used as a CtTypeReference), test with both `CtTypeReference` objects AND `String` objects as the parameter value
- Common pitfalls to avoid:
  - Testing only one type of parameter value (e.g., only `String`) when the method accepts `Object` and handles multiple types
  - Assuming the parameter will always be of a particular type without verifying the type
  - Not testing edge cases where the parameter value is of an unexpected but valid type
  - Not catching a `ClassCastException` that occurs when the code casts the `Object` parameter to a specific type without a type check

### Correct Example (Java-like pseudocode):
```java
// BUGGY: Assumes parameter is always CtTypeReference
CtTypeReference ref = (CtTypeReference) params.get("$class$");  // ClassCastException when String is passed

// FIXED: Checks type before casting
Object classParam = params.get("$class$");
if (classParam instanceof CtTypeReference) {
    CtTypeReference ref = (CtTypeReference) classParam;
} else {
    // handle String or other type
}

// Test that catches the bug:
@Test
public void testProxyWithStringParameter() {
    Map<String, Object> params = new HashMap<>();
    params.put("$class$", "java.lang.String");  // String type, not CtTypeReference
    assertThrows(ClassCastException.class, () -> buggyProcessor.process(params));
}

@Test  
public void testProxyWithCtTypeRefParameter() {
    Map<String, Object> params = new HashMap<>();
    params.put("$class$", mock(CtTypeReference.class));  // CtTypeReference type
    assertDoesNotThrow(() -> fixedProcessor.process(params));
}
```

### Incorrect Example (what a naive TG might write):
```java
// INCOMPLETE: Only tests with CtTypeReference, misses the String case
@Test
public void testProxyParameter() {
    Map<String, Object> params = new HashMap<>();
    params.put("$class$", mock(CtTypeReference.class));
    processor.process(params);  // passes with fix, but doesn't detect the bug
}
```