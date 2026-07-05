---
name: form-element-parameter-type-validation
description: When a form element stores parameters in a map keyed by Class<?> type,
  the TG should test with parameters of different types to verify the parameter is
  retrievable by its exact type. This catches bugs where parameters registered with
  one type are stored under a different type key.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# form-element-parameter-type-validation

## Instructions

# Form Element Parameter Type Validation

## Instructions

- WHEN a code form element (such as `AbstractFormElement`) maintains an internal `Map<Class<?>, Object>` for storing typed parameters, and it exposes a method to set a parameter (e.g., `setParameter(Class<T> type, T value)`) and a method to get a parameter (e.g., `getParameter(Class<T> type)`)
- THEN the TG should write a parameterized state test that:
  1. Creates an instance of the form element
  2. Calls the setter with a parameter registered under a specific type (e.g., `String.class`)
  3. Calls the getter with the same type (`String.class`)
  4. Verifies that the returned value is the same object that was set (assertSame or equals)
  5. Then also tests with a different but compatible type (e.g., `Object.class`) to verify that the getter returns `null` when no parameter was registered for that exact type
- Common pitfalls:
  - Testing only with the setter method without verifying the getter's behavior
  - Assuming the getter can retrieve the parameter using a supertype (e.g., `Object.class`) when it was registered with a subtype (e.g., `String.class`)
  - Not testing with multiple type parameters (e.g., both `String` and `Integer`) to ensure independent storage
- Example:
  ```java
  // Correct test pattern
  @Test
  public void testParameterByExactType() {
      AbstractFormElement element = new AbstractFormElement("test");
      element.setParameter(String.class, "hello");
      assertSame("hello", element.getParameter(String.class));
      assertNull(element.getParameter(Object.class));
  }
  ```
- Incorrect test pattern:
  ```java
  // Wrong: only testing the setter side effect, not verifying getter
  @Test
  public void testSetParameter() {
      AbstractFormElement element = new AbstractFormElement("test");
      element.setParameter(String.class, "hello");  // no assertion on getter
  }
  ```