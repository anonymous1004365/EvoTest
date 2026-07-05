---
name: executable-reference-type-validation
description: When creating executable references (e.g., constructor references like
  `this::new`), the test must validate that correct types (CtTypeReference, not raw
  String or wrong type) are used to build the reference. Without proper type selection,
  the reference silently fails or uses the wrong declaring type.
code_tags:
- TYPE_CONVERSION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# executable-reference-type-validation

## Instructions

# Executable Reference Type Validation

## Instructions

- WHEN the TG encounters code that creates executable references (e.g., `ExecutableReference`) using a candidate type (like `CtTypeReference`), such as in a method like `createReference` or `executableReferenceFor` that receives a type parameter which could be a `String`, `CtTypeReference`, or other representation:
  - THEN the TG should write a test that passes **different kinds of types** (e.g., a `CtTypeReference` for an anonymous class, a `CtTypeReference` for a named class) and verifies the resulting `ExecutableReference` has the **correct declaring type**.
  - Specifically, when the code is creating a reference for an **anonymous executable** (e.g., `this::new` inside an anonymous class body), verify that the declaring type in the resulting `ExecutableReference` matches the anonymous class type, not some other type.
  - The test should catch cases where the wrong type variable is used (e.g., using the enclosing class's type instead of the anonymous type), which would cause incorrect behavior like failing to match or resolve the reference.

- WHEN the code being tested selects a type from a list or collection of candidates (e.g., iterating over potential declaring types):
  - THEN test with at least two candidates where one matches and one doesn't, and verify that the correct (matching) one is selected.
  - Common pitfalls: A test that only provides a single candidate type cannot detect selection bugs where the wrong candidate is chosen (e.g., always picking the first or last instead of the matching one).

- WHEN testing executable reference creation with anonymous classes (lambda-like or anonymous inner classes):
  - THEN create a test class that contains an anonymous class definition, and obtain a `CtTypeReference` to that anonymous class.
  - Use that reference as the candidate when creating the executable reference.
  - Verify the reference's declaring type equals the anonymous class type.

- Example of a correct test:
```java
@Test
public void testAnonymousExecutableReference() {
    // Build a factory that creates references, passing the anonymous type
    CtTypeReference<?> anonymousType = ...; // obtained from factory
    ExecutableReference ref = factory.createReference(anonymousType);
    
    // Verify the declaring type is the anonymous type, not the enclosing type
    assertEquals(anonymousType, ref.getDeclaringType());
}
```

- Example of a common mistake (weak test that misses the bug):
```java
@Test
public void testExecutableReference() {
    // Only testing with a named class — will not catch anonymous type bugs
    ExecutableReference ref = factory.createReference(someNamedType);
    assertNotNull(ref); // Too weak — passes even with wrong type
}
```

- The key insight: the bug occurs when multiple type candidates exist and the code selects the wrong one (e.g., the outer class instead of the anonymous inner class). Your test must ensure the selection logic picks the correct type.