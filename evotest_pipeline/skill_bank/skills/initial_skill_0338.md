---
name: template-parameter-type-validation
description: When validating proxy template parameters that can accept multiple types (e.g., String and CtTypeReference), test with all expected parameter types to ensure the validation path supports each type correctly. The TG should verify that no UnsupportedOperationException or similar errors occur for any supported parameter type.
code_tags: ['ALTERNATIVE_PROTOCOL_DECODING', 'COLLECTION_ITERATION', 'VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that processes a collection of parameters/arguments that can be of **multiple different types** (e.g., a List containing both `String` objects and `CtTypeReference` objects, or similar heterogeneous collections), and the method iterates over these elements performing type-specific operations:

  - THEN the TG should write a test that provides **each supported parameter type** to verify all branches of type discrimination logic work correctly.
  - For each parameter type, the test should verify that the method under test does **not** throw `UnsupportedOperationException` or `ClassCastException`.
  - The test should specifically try to add **template parameters** (e.g., proxy parameters or generic type arguments) of different types to the collection, then invoke the validation/processing method.
  - Verify that for each distinct type in the collection, the method correctly handles it without throwing an exception.

- WHEN the code under test uses `instanceof` checks followed by type-specific logic (e.g., `if (param instanceof String) { ... } else if (param instanceof CtTypeReference) { ... }`) and a type is not handled, leading to fallthrough to a default case that throws an exception:

  - THEN the TG should identify **all possible runtime types** that can appear in the collection by examining how parameters are added in production code paths.
  - Write a parametric test that exercises each type variant explicitly.

- Common pitfalls to avoid:
  - Testing only with `String` type parameters when the collection also accepts `CtTypeReference` or other types at runtime.
  - Testing the method in isolation without first populating the collection with parameters of different types.
  - Assuming the method throws an exception only for null/invalid input — it may also throw for valid but unhandled types.
  - Not checking the exception message or type in assertions — use `assertThrows(UnsupportedOperationException.class, ...)` or verify no exception is thrown.

## Example

**Correct test** (catches the bug):
```java
@Test
public void testValidateWithMultipleParameterTypes() {
    // Create the component with proxy parameters of different types
    CtModel model = new CtModelImpl();
    CtClass<?> proxy = model.addClass("MyProxy");
    
    // Add a String parameter
    proxy.addParam("type1", "java.lang.String");
    
    // Add a CtTypeReference parameter
    CtTypeReference<?> typeRef = model.createTypeReference();
    proxy.addParam("type2", typeRef);
    
    // This should NOT throw for either parameter type
    assertDoesNotThrow(() -> proxy.validate());
}
```

**Incorrect test** (misses the bug):
```java
@Test
public void testValidateWithStringParams() {
    CtModel model = new CtModelImpl();
    CtClass<?> proxy = model.addClass("MyProxy");
    proxy.addParam("type1", "java.lang.String");
    
    // Only tests String type — misses CtTypeReference handling failure
    assertDoesNotThrow(() -> proxy.validate());
}
```