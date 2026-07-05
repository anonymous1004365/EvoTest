---
name: generic-method-reference-type-resolution
description: When testing code that resolves references to generic methods, the TG should verify that method references and type parameters are correctly resolved. Generic type parameters (like T) should not be confused with concrete types (like CtTypeReference to the parameter), and the test should exercise the full resolution chain including the declaring executable lookup.
code_tags: ['ARGUMENT_VALIDATION', 'NULL_CHECK', 'STRING_PARSING', 'TYPE_REFERENCE_EQUALS']
test_pattern: STATE_TEST
---

# generic-method-reference-type-resolution

## Instructions

# Generic Method Reference Type Resolution

## Instructions

- WHEN the TG encounters code that resolves executable references (CtExecutableReference) for generic methods — especially methods that have their own type parameters (e.g., `<T> void foo(T param)`)
- THEN the TG should write a test that:
  1. Creates a reference to a generic method declared **outside** the referencing class (i.e., the method is on a different class than the one making the reference)
  2. The test should verify that calling getDeclaringExecutable() on the referencing element returns a valid (non-null) result
  3. The test should verify that the actual declaration of the generic method can be correctly resolved from the reference
  4. WHEN the buggy version might return null for such references, the test should assert that the resolved executable is not null

- Common pitfalls to avoid:
  - Testing only references where the generic method is in the **same** class — this may not trigger the resolution edge case
  - Testing only non-generic method references — the bug specifically involves generic type parameters
  - Assuming that `getDeclaringExecutable()` returns a valid result without checking — the buggy version may return null for cross-class generic method references
  - Using only a single type of parameter (e.g., only `String`) — test with both a generic type parameter `T` and a concrete type parameter to ensure correct resolution in both cases

- Example of a correct test:
```java
// Given a class with a generic method:
// class Provider {
//     public <T> T provide(Class<T> type) { ... }
// }
// And a class that references it:
// class User {
//     public void use() {
//         Provider p = new Provider();
//         p.provide(String.class); // This creates a reference to the generic method
//     }
// }
// Then test:
@Test
public void testGenericMethodReferenceFromOutsideClass() {
    CtClass<?> userClass = launcher.getFactory().Class().get("User");
    CtMethod<?> useMethod = userClass.getMethodsByName("use").get(0);
    CtExecutableReference<?> ref = ...; // get the reference created inside use()
    CtExecutable<?> declaration = ref.getDeclaringExecutable();
    assertNotNull("Generic method declared in another class must be resolvable", declaration);
}
```

- Example of an incorrect test (that would miss the bug):
```java
// BAD: Only tests non-generic references from the same class
@Test
public void testMethodReference() {
    CtClass<?> clazz = launcher.getFactory().Class().get("SameClass");
    CtExecutableReference<?> ref = clazz.getMethodsByName("bar").get(0).getReference();
    assertNotNull(ref.getDeclaringExecutable()); // This works, but doesn't cover the generic cross-class case
}
```