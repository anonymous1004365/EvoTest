---
name: superclass-type-mismatch-on-null
description: When querying class hierarchy information (e.g., getSuperclass), the
  method may incorrectly return a non-null TypeReference wrapping a null actual type
  instead of returning null. Apply this skill to test methods that return class/type
  references for scenarios where a class has no superclass (e.g., java.lang.Object
  or interfaces).
code_tags:
- TYPE_CONVERSION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# superclass-type-mismatch-on-null

## Instructions

# Superclass Type-Reference Mismatch on Null

## Instructions

- WHEN the TG encounters a method that returns a `CtTypeReference` (or similar type reference wrapper) for a class hierarchy query (e.g., `getSuperclass`, `getSuperInterface`), and the result might be `null` (e.g., for `java.lang.Object` or for an interface),
- THEN the TG should write a test that:
  1. Calls the method on the special case that should return `null` (e.g., `java.lang.Object`'s superclass, or an interface's superclass).
  2. Asserts that the actual return value is `null` — NOT a `CtTypeReference` whose internal type field is `null`.
  3. If the method is expected to throw an exception for such cases, verify the correct exception type.
- Common pitfalls:
  - Testing only with "normal" classes that do have a superclass (e.g., `String` → `Object`), and never testing the `null` boundary case.
  - Writing an assertion like `assertNotNull(superclass)` which passes on the buggy version if a non-null wrapper containing a null type is returned.
  - Writing assertions that only compare `toString()` output, which may be the same ("null") for both a real null and a wrapper holding null.
- Example correct test (pseudocode):
  ```java
  // For java.lang.Object, getSuperclass() should return null
  CtTypeReference<?> superclass = factory.Type().get(Object.class).getSuperclass();
  assertNull("Object should have no superclass", superclass);
  ```
- Example incorrect test (would pass on buggy version too — too weak):
  ```java
  // This assertion passes even if a non-null wrapper with null inside is returned
  CtTypeReference<?> superclass = factory.Type().get(Object.class).getSuperclass();
  assertNull("Should be null", superclass == null ? null : superclass.getActualType()); // Wrong approach
  ```
- Example incorrect test (misses the bug entirely):
  ```java
  // Only tests a class that has a superclass — never hits the null boundary
  CtTypeReference<?> superclass = factory.Type().get(String.class).getSuperclass();
  assertEquals("java.lang.Object", superclass.getQualifiedName()); // Passes in both buggy and fixed
  ```