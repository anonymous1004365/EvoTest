---
name: cloned-reference-stale-metadata
description: When cloning object references that carry metadata fields (e.g., field
  or type references in AST/reflection), the clone must also update metadata to reflect
  the new container. Without updating after clone, methods like getDeclaration() may
  fail because stale metadata points to a different owner.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# cloned-reference-stale-metadata

## Instructions

# Cloned Reference Must Update Metadata After Clone

## Instructions

- WHEN the TG encounters code that clones an object reference (e.g., `CtFieldReference`, `CtTypeReference`, `CtExecutableReference`) that carries additional metadata/qualifier fields (like `field.getType()`, `field.getDeclaringType()`, `type.getPackage()`, `type.getDeclaringType()`), and the clone is subsequently used to look up declarations via methods like `getDeclaration()`, `getTypeDeclaration()`, etc.

- THEN the TG must write a test that:
  1. Creates the original reference (e.g., via `factory.Type().get(String.class)` or `factory.Field().get(SomeClass.class, "fieldName")`)
  2. Creates a clone (e.g., `ref.clone()` or `ref.clone(processor)`)
  3. Asserts that the cloned reference's metadata fields (e.g., `getDeclaringType()`, `getPackage()`, `getType()`) match the expected clone identity, NOT the original's identity
  4. Calls `getDeclaration()` on the cloned reference and verifies it returns the correct (non-null) declaration
  5. The test must compare the cloned reference to the original and ensure state mutation (like `declaringType`) was properly updated

- Common pitfalls to avoid:
  - Testing only `toString()` or `equals()` — these do not verify declaration lookup
  - Assuming `clone()` is a deep copy of all fields — metadata fields may be shallow-copied and left stale
  - Not testing the actual declaration lookup after cloning — getDeclaration() relies on internally cached metadata that must match the cloned object's identity
  - Testing only one type of reference (e.g., only `CtTypeReference`) — all reference types with metadata are at risk

- **Correct example:**
```java
// Given: A CtTypeReference for java.lang.String
CtTypeReference<String> stringRef = factory.Type().get(String.class);
// When: We clone it (e.g., by setting it as a field type)
CtTypeReference<?> clonedRef = stringRef.clone();  // or similar clone operation
// Then: getDeclaration() on the clone should NOT return null
assertNotNull(clonedRef.getDeclaration());  // This fails if stale metadata remains
// And: The clone should not point to the same metadata as the original
assertNotSame(stringRef.getPackage(), clonedRef.getPackage());  // if package ref was shallow-copied
```

- **Incorrect example (will not catch the bug):**
```java
// BAD: Only checks equality, does not exercise declaration lookup
CtTypeReference<String> ref = factory.Type().get(String.class);
CtTypeReference<?> clone = ref.clone();
assertEquals(ref, clone);                // This passes even when getDeclaration() is broken
assertEquals(ref.toString(), clone.toString()); // Also passes with stale metadata
// Missing: getDeclaration() is never called, so the bug is invisible
```