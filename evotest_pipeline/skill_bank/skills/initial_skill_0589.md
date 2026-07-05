---
name: clone-declaration-binding
description: When a reference is cloned, its internal declaration binding may be lost
  or detached. Tests should verify that cloned references still resolve to the correct
  original declaration.
code_tags:
- ARGUMENT_VALIDATION
- ARRAY_INDEX_ACCESS
- STATE_MUTATION
test_pattern: STATE_TEST
---

# clone-declaration-binding

## Instructions

# Cloned Reference Declaration Binding

## Instructions

- WHEN the TG encounters code where an AST element (like `CtTypeReference`, `CtFieldReference`, `CtExecutableReference`) implements a `clone()` method that creates a shallow copy
- AND the cloned reference's `declaration` or `getDeclaration()` field is not explicitly re-resolved or re-assigned after cloning (e.g. `clone()` on a CtReference subclass does not copy the `declaration` field)
- THEN the TG MUST write a test that:
  1. Obtains a reference to an actual declaration (e.g., via `Factory.Type().get(SomeClass.class).getReference()` or `getDeclaringType()`)
  2. Calls `getDeclaration()` on the original reference to confirm it is non-null
  3. Clones the reference (e.g., `reference.clone()`)
  4. Calls `getDeclaration()` on the **cloned** reference
  5. **Asserts** that the cloned reference's `getDeclaration()` returns the same non-null declaration as the original (using `assertNotNull` and `assertEquals` / `assertSame`)
  6. **Important**: The test should deliberately fail on the buggy version (where `getDeclaration()` returns `null` after clone) and pass on the fixed version

- **Common pitfalls to avoid**:
  - Do NOT assume that `clone()` preserves all state — the `declaration` field is often `transient` or set to `null` in `clone()` implementations of CtReference subclasses
  - Do NOT test only the original reference — the bug is specifically about the **clone's** behavior
  - Do NOT mock the factory or the reference — the test must use real CtElement instances to exercise the actual `clone()` implementation
  - Do NOT forget to use `assertNotNull` — on the buggy version the declaration will be null on the clone, not an incorrect value

- **Example (correct test)**:
```java
// Correct: tests that cloned reference retains declaration binding
@Test
public void testGetDeclarationOfFieldAfterClone() {
    // given
    CtType<?> type = factory.Type().get(SomeClass.class);
    CtField<?> field = type.getField("someField");
    CtFieldReference<?> fieldRef = field.getReference();
    CtFieldReference<?> clonedRef = fieldRef.clone();
    
    // then
    assertNotNull(fieldRef.getDeclaration()); // original works
    assertNotNull(clonedRef.getDeclaration()); // clone must also work
    assertEquals(fieldRef.getDeclaration(), clonedRef.getDeclaration());
}
```

- **Example (incorrect test — would NOT catch the bug)**:
```java
// WRONG: only tests the original, not the clone
@Test
public void testFieldReference() {
    CtFieldReference<?> ref = ...;
    assertNotNull(ref.getDeclaration()); // passes even on buggy version
    // Missing: clone() and test clone's getDeclaration()
}
```