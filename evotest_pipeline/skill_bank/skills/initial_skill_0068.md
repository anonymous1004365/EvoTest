---
name: generic-method-reference-type-resolution
description: When testing code that resolves method references to generic methods,
  verify that the type arguments of the generic method declaration are preserved and
  matched correctly. This skill helps catch bugs where the returned method reference
  has incompatible generic type parameters.
code_tags:
- ARGUMENT_VALIDATION
- CONDITIONAL_BRANCH
- STATE_TRANSITION
- GENERIC_METHOD_REFERENCE
- TYPE_CONVERSION
- VALIDATION
test_pattern: STATE_TEST
---

# generic-method-reference-type-resolution

## Instructions

# Generic Method Reference Type Resolution

## Instructions

- WHEN the TG encounters code that resolves a method reference (e.g., via `ExecutableReference` or similar API) and the referenced method is generic (has type parameters like `<T>`)
- THEN the TG should test that the resolved method reference preserves the correct generic type information from the actual method declaration, not from an unrelated or incorrect source
- Specifically, when testing method references like `List::of` (which returns `List<T>`), verify that the returned method reference's generic method (e.g., `getGenericMethod()`) matches the declared generic method of the target class with the CORRECT type parameter (e.g., `<T>`) — NOT a different type like `<E>` from an unrelated method
- The test should:
  1. Obtain a method reference from a source (e.g., a `CtTypeReference` or similar)
  2. Retrieve the generic method from that reference (e.g., via `getGenericMethod()`)
  3. Assert that the generic method's type parameter (e.g., the name of the type variable) matches the expected one from the actual declaration
  4. The test on the buggy version should FAIL — the returned generic method type parameter will be incorrect (e.g., `<E>` instead of `<T>`)

- Common pitfalls to avoid:
  - Do NOT test only that the method reference is non-null or has the right name — this misses the type parameter mismatch
  - Do NOT assume the type parameter of the returned generic method is correct without checking its actual name/signature
  - Do NOT compare against a hardcoded expected method — use the actual declared method from the target class to dynamically assert correctness

- Example (correct):
```java
// Given a method reference to a generic method like List::of
// Verify the type parameter of the generic method returned
import java.lang.reflect.Method;
import java.lang.reflect.TypeVariable;  

CtMethod<?> genericMethod = methodReference.getGenericMethod();
// Get the first type parameter
TypeVariable<?>[] typeParams = genericMethod.getActualClass().getDeclaredMethod("of", ...).getTypeParameters();
assertEquals("T", typeParams[0].getName());  // List.of uses <T>
```

- Example (incorrect — too weak to catch the bug):
```java
// WRONG: Only checks existence, not type parameter correctness
assertNotNull(methodReference.getGenericMethod());
assertEquals("of", methodReference.getGenericMethod().getSimpleName());
// Missing: check that the type parameter is <T> not <E>
```