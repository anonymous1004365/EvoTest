---
name: nullable-type-reference-validation
description: When processing imported type references that may be null (e.g., CtTypeReference.getTypeDeclaration()),
  test that the code handles null instead of throwing NullPointerException. This skill
  applies when methods iterate over imports and call methods on potentially null type
  references.
code_tags:
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# nullable-type-reference-validation

## Instructions

# Nullable Type Reference Validation

## Instructions

- WHEN the TG encounters code that retrieves type references (e.g., `CtTypeReference`) from imports or scanning context and calls methods on them (e.g., `getTypeDeclaration()`, `getSimpleName()`, `getQualifiedName()`)
- THEN the TG should test with a null type reference scenario: create or encounter a `CtTypeReference` whose referencing object (e.g., `CtTypedElement.getType()`) returns `null`, or whose `getTypeDeclaration()` returns `null`, and verify the code handles this gracefully instead of throwing a `NullPointerException`
- Include in the test a scenario where an import or type reference could be null — for example, a reference obtained from a `CtImport` or from iterating over imports where the import kind might not have a corresponding type declaration
- The test should verify that on the buggy version, a `NullPointerException` is thrown (or the code fails), while on the fixed version, the null case is handled (e.g., by a null check, an `if (ref != null)` guard, or skipping the element)
- Common pitfalls to avoid:
  - Testing only with valid/complete type references and missing the null case
  - Assuming `getTypeDeclaration()`, `getType()`, or similar methods always return non-null
  - Only testing the "happy path" where all imports resolve to actual types
  - Not testing with a `CtImport` or similar object that has a null type reference

### Example (Correct — tests null reference):

```java
@Test
public void testWithNullTypeReference() {
    // Arrange: create a mock import that returns null for its type reference
    CtImport mockImport = mock(CtImport.class);
    CtTypeReference nullRef = null;
    when(mockImport.getTypeReference()).thenReturn(nullRef);
    
    // Act & Assert: should not throw NullPointerException
    List<CtImport> imports = new ArrayList<>();
    imports.add(mockImport);
    assertDoesNotThrow(() -> methodUnderTest(imports));
}
```

### Example (Incorrect — only tests non-null references):

```java
@Test
public void testImports() {
    // WRONG: Only creates valid imports, never tests null reference scenario
    CtImport validImport = createValidImport("java.util.List");
    List<CtImport> imports = Arrays.asList(validImport);
    
    // This passes on both buggy and fixed versions — misses the null bug!
    methodUnderTest(imports);
}
```