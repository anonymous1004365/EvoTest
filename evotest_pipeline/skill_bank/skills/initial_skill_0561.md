---
name: diamond-operator-type-inference-validation
description: WHEN the TG encounters code involving generic type inference with the
  diamond operator (e.g., new HashMap<>()) in the context of CtTypeReference / type
  access nodes, THEN it should test that inferred type arguments are properly resolved
  and stored, not silently lost or replaced with defaults. Apply this skill when validating
  type arguments in AST node construction.
code_tags:
- TYPE_CONVERSION
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# diamond-operator-type-inference-validation

## Instructions

# Diamond Operator Type Inference Validation

## Instructions

- **WHEN** the TG encounters a method that processes generic type arguments containing diamond operators (`<>`) in Java, such as resolving `new HashMap<>()` where the type arguments must be inferred from the context  
- **THEN** it should write a test that programmatically constructs or parses a generic type with diamond inference, accesses the inferred type arguments via `CtTypeReference.getActualTypeArguments()`, and asserts that the type arguments are present (non-empty) and match the expected inferred types  
- **WHEN** the code under test is responsible for converting or migrating type references between AST nodes (e.g., building a type access from a type reference)  
- **THEN** the test should verify that the type argument conversion is complete by asserting both the size and content of the actual type arguments list, not just that the resulting object is non-null  
- **Common pitfalls to avoid**  
  - Testing only that no exception is thrown when processing diamond operators — this misses silently dropped type arguments  
  - Verifying only the top-level type (e.g., `Map`) without checking that the inferred type parameters (e.g., `String`, `String`) survived conversion  
  - Using only compile-time constant generics like `List<String>` — diamond-based inference is a distinct code path that behaves differently  

### Correct Example (catches the bug)
```java
// Construct a generic type using diamond inference (e.g., new HashMap<>())
// Then resolve its type reference and check actual type arguments
CtTypeReference<?> ref = ...; // type reference that used <>
List<CtTypeReference<?>> typeArgs = ref.getActualTypeArguments();
assertFalse("Diamond-inferred type should have type arguments", typeArgs.isEmpty());
assertEquals("Expected 2 type arguments for Map<String, String>", 2, typeArgs.size());
assertEquals(String.class.toString(), typeArgs.get(0).getQualifiedName());
assertEquals(String.class.toString(), typeArgs.get(1).getQualifiedName());
```

### Incorrect Example (misses the bug)
```java
// Only checking that the type reference is non-null
CtTypeReference<?> ref = ...;
assertNotNull("Type reference should exist", ref);
// Bug: type arguments were silently dropped but this assertion passes
```