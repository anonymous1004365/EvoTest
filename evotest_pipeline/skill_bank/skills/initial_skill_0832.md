---
name: view-message-factory-missing-response-type
description: When a ViewMessageFactory has a createUnregisterResponse(String) method
  that only handles String parameters but not CtTypeReference parameters, the TG should
  test both parameter types to catch the missing handler logic.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- BOUNDARY_CHECK
- VIEW_MESSAGE_FACTORY_MISSING_RESPONSE_TYPE
test_pattern: EXCEPTION_TEST
---

# view-message-factory-missing-response-type

## Instructions

# ViewMessageFactory Missing Response Type Handler

## Instructions

- WHEN the TG encounters a `ViewMessageFactory` class (or similar factory class) that contains methods like `createUnregisterResponse`, `createRegisterResponse`, or similar response-creation methods that accept a `String` parameter (e.g., `createUnregisterResponse(String param)`)
- THEN the TG should also test with a `CtTypeReference` parameter type if the class has any overloads or type-agnostic parameter handling — specifically, call the same method name with a `CtTypeReference` argument (e.g., `CtTypeReference<?>` or a concrete implementation) and verify that:
  1. No `ClassCastException` is thrown when processing the parameter
  2. The method correctly handles the `CtTypeReference` type without assuming the parameter is always a `String`
  3. The returned result is not null and has the expected structure
- Common pitfalls to avoid:
  - Testing only with `String` parameters when the factory may also accept `CtTypeReference` objects
  - Writing assertions only for the String case and assuming type handling is generic
  - Failing to check for `ClassCastException` on methods that internally cast the parameter without type-checking

### Correct Example (should detect the bug):
```java
@Test
public void createUnregisterResponse_withCtTypeReference_shouldNotThrow() {
    ViewMessageFactory factory = new ViewMessageFactory();
    CtTypeReference<?> typeRef = mock(CtTypeReference.class);
    // Should not throw ClassCastException
    ResponseMessage response = factory.createUnregisterResponse(typeRef);
    assertNotNull(response);
}
```

### Incorrect Example (would miss the bug):
```java
@Test
public void createUnregisterResponse_withString_works() {
    ViewMessageFactory factory = new ViewMessageFactory();
    ResponseMessage response = factory.createUnregisterResponse("someString");
    assertNotNull(response);
}
```

The buggy version of `ViewMessageFactory.createUnregisterResponse(String)` may internally process the parameter by casting it to an incompatible type, or may route through a code path that fails when the argument is not a `String`. The test with `CtTypeReference` will trigger a `ClassCastException` that should not occur.