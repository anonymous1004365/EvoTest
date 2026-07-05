---
name: generic-type-signature-matching
description: When testing type signature comparison methods that involve generic types,
  identify cases where type arguments are used (e.g., List<String> vs List<Integer>)
  and verify that the method correctly distinguishes them as different signatures.
  This skill applies to any method that compares type references or method signatures
  involving parameterized types.
code_tags:
- TYPE_CONVERSION
- BOUNDARY_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# generic-type-signature-matching

## Instructions

# Generic Type Signature Matching

## Instructions

- WHEN the TG encounters a method that compares type references or method signatures (e.g., `isSameSignature`, `isSubtype`, `equals` on `CtTypeReference`), especially when generic/parameterized types are involved (e.g., `List<String>`, `Map<String, Integer>`)
- THEN the TG should write tests that:
  1. Create two type references with different type arguments but the same base type (e.g., `CtTypeReference` for `List<String>` vs `CtTypeReference` for `List<Integer>`)
  2. Verify that they are NOT considered the same signature — they should NOT match because `List<String>` and `List<Integer>` are different parameterized types
  3. Also test that the same parameterized type against itself DOES match (e.g., `List<String>` vs `List<String>` should return true)
  4. Test edge cases: raw types without generics vs parameterized types (e.g., `List` vs `List<String>`), unbounded wildcards vs specific types
  5. Include both positive cases (should match: same parameterized type) and negative cases (should not match: different type arguments)
- Common pitfalls to avoid:
  - Only testing with simple (non-generic) types — the bug surfaces specifically with parameterized types
  - Forgetting to compare type arguments/actual type parameters, only comparing the base type
  - Assuming that all generic type comparisons work the same way — the implementation might match on base type name only, ignoring type arguments
  - Not creating proper `CtTypeReference` instances with type arguments set up correctly

### Correct Example (should match):
```java
// Two references to the same parameterized type: List<String>
CtTypeReference<?> listString1 = factory.Type().createReference(List.class);
listString1.setActualTypeArguments(factory.Type().createReference(String.class));
CtTypeReference<?> listString2 = factory.Type().createReference(List.class);
listString2.setActualTypeArguments(factory.Type().createReference(String.class));
// These should match — same base type and same type argument
assertTrue(listString1.isSameSignature(listString2));
```

### Correct Example (should NOT match — catches the bug):
```java
// List<String> vs List<Integer> — different type arguments
CtTypeReference<?> listString = factory.Type().createReference(List.class);
listString.setActualTypeArguments(factory.Type().createReference(String.class));
CtTypeReference<?> listInteger = factory.Type().createReference(List.class);
listInteger.setActualTypeArguments(factory.Type().createReference(Integer.class));
// These should NOT match — different type arguments
assertFalse(listString.isSameSignature(listInteger));
```

### Incorrect Example (would miss the bug):
```java
// Only testing non-generic types — does NOT exercise the type-argument comparison
CtTypeReference<?> stringRef = factory.Type().createReference(String.class);
CtTypeReference<?> stringRef2 = factory.Type().createReference(String.class);
assertTrue(stringRef.isSameSignature(stringRef2)); // OK, but skips the bug entirely
```