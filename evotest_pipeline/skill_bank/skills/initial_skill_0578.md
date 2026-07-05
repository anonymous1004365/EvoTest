---
name: primitive-type-access-validation
description: When dealing with type access on primitive types (e.g., int, void), the
  TG should test that accessing types like CtTypeAccess on primitives with type references
  does not produce a NullPointerException or ClassNotFoundException, ensuring the
  type reference system handles primitives gracefully.
code_tags:
- TYPE_CONVERSION
- VALIDATION
- PRIMITIVE_TYPE_ACCESS
test_pattern: EXCEPTION_TEST
---

# primitive-type-access-validation

## Instructions

# Primitive Type Access Validation

## Instructions

- WHEN the code involves computing a type access (e.g., `CtTypeAccess`) from a type reference, and the type reference may represent a primitive type (e.g., `int`, `void`, `boolean`), or a wrapper type (e.g., `Integer`), 
- THEN the test MUST verify that no `NullPointerException` or `ClassNotFoundException` is thrown when a `CtTypeReference` pointing to a primitive type (e.g., `int`) is used to resolve the actual type.
- Specifically, WHEN creating a `CtTypeReference` from a class like `Integer.class` or `int.class`, the test MUST also use `factory.Type().createReference(int.class)` (or similar) to obtain a `CtTypeReference` whose `getActualClass()` returns `Integer.TYPE` (the primitive `int` wrapper class). THEN the test MUST call the method that creates a type access from that reference and assert that the result is not null and that no exception is thrown.
- Common pitfalls: 
  - Testing only with regular class types (e.g., `String`, `List`) while ignoring primitive types.
  - Testing only with `void` but not with other primitives like `int`, `boolean`, `char`, etc.
  - Not checking that the returned `CtTypeAccess` is non-null.
  - Assuming that `CtTypeReference.getActualClass()` always returns a non-primitive class.
- Example of correct test (using the same pattern as the triggering test):
  ```java
  @Test
  public void testTypeAccessOnPrimitive() {
      // Using a TypeReference for a primitive type
      CtTypeReference<Integer> typeRef = factory.Type().createReference(int.class);
      // This should NOT throw NullPointerException
      CtTypeAccess<Integer> typeAccess = factory.Type().createTypeAccess(typeRef);
      assertNotNull(typeAccess);
      
      // Also test with void
      CtTypeReference<Void> voidRef = factory.Type().createReference(void.class);
      CtTypeAccess<Void> voidAccess = factory.Type().createTypeAccess(voidRef);
      assertNotNull(voidAccess);
  }
  ```
- Example of INCORRECT test (what the TG might write without this skill):
  ```java
  // WRONG: only tests with non-primitive type
  @Test
  public void testTypeAccessOnString() {
      CtTypeReference<String> typeRef = factory.Type().createReference(String.class);
      CtTypeAccess<String> access = factory.Type().createTypeAccess(typeRef);
      assertNotNull(access);
  }
  // This test would pass even on buggy code, missing the primitive bug entirely.
  ```