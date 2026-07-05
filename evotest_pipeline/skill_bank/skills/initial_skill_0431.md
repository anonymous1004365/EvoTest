---
name: stub-mock-parameter-type-validation
description: When a method accepts Object parameters but internally treats them as
  String, test with both String and non-String types (like CtTypeReference) to catch
  ClassCastException. This skill prevents the TG from only testing valid String inputs.
code_tags:
- NULL_CHECK
- VALIDATION
- PARAMETER_TYPE_VALIDATION
test_pattern: EXCEPTION_TEST
---

# stub-mock-parameter-type-validation

## Instructions

# Stub and Mock Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that accepts `Object` typed parameters (e.g., `checkStubAndMock(Object value)`) but the method body performs a direct cast to `String` like `(String) value` without any `instanceof` type check
- THEN the TG should write a test that passes a non-String object (e.g., a class object like `CtTypeReference.class`, an Integer, or any custom type) to the method, and verify that the buggy version throws a `ClassCastException`. The test should also verify that the fixed version does NOT throw (i.e., the call succeeds without exception when the fix adds proper `instanceof` checking and conversion logic)
- Include what mistakes to avoid: Common pitfalls include (1) only testing with valid String inputs which pass on both buggy and fixed versions, (2) forgetting to assert that the fixed version actually works correctly after the instanceof check, (3) not testing with null values if the method has no null guard, (4) assuming the method parameter type in the signature (e.g., `Object`) means any type is safe to pass.

Examples:

Correct test (catches the bug):
```java
@Test
public void testCheckStubAndMockWithNonString() {
    // This triggers ClassCastException on buggy version
    AbstractInterfaceConfig config = new AbstractInterfaceConfig();
    // Pass a Class<?> object instead of a String
    config.checkStubAndMock(CtTypeReference.class);
    // If the fix is correct, no exception should be thrown
}
```

Incorrect test (misses the bug):
```java
@Test
public void testCheckStubAndMockWithString() {
    // This passes on both buggy and fixed versions
    AbstractInterfaceConfig config = new AbstractInterfaceConfig();
    config.checkStubAndMock("someString");
    // Test passes even on buggy code
}
```