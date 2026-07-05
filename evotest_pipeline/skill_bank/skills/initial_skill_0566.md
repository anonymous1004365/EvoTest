---
name: type-reference-qualified-name-number-prefix
description: WHEN validating that all type references to a local type produce correct
  qualified names, test that qualifiers do not start with numeric characters. A local
  type's qualified name may unexpectedly include a numeric prefix from its parent,
  causing incorrect string representations for type references.
code_tags:
- NULL_CHECK
- VALIDATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# type-reference-qualified-name-number-prefix

## Instructions

# Type Reference Qualified Name Validation for Local Types

## Instructions

- WHEN the TG encounters code that resolves the **qualified name** of a `CtTypeReference` (e.g., `getQualifiedName()`, `getSimpleName()`, or any method that returns a string representation of a type reference), especially for local/anonymous types declared inside methods or blocks
- THEN the TG should test that **all** `CtTypeReference` elements pointing to the same local type produce **identical** qualified names, and that none of those qualified names start with a numeric character (e.g., `"1"`, `"2"`, etc.)
- Include a test that:
  1. Creates a local type inside a method (e.g., a local class or interface declared within a method body)
  2. Retrieves **all type references** to that local type from the model (e.g., from all `CtTypeReference` elements in the factory or from a specific scope like field types, parameter types, or return types)
  3. For each reference, calls `getQualifiedName()` and verifies the result does NOT match a regex like `^[0-9]` — i.e., the qualified name should not start with a digit
  4. Verifies that all references to the same local type yield the same qualified name
- Common pitfalls:
  - **Testing only the simple name**: The bug affects `getQualifiedName()` — testing only `getSimpleName()` would miss it. Always test the full qualified name.
  - **Testing only one reference**: If a local type appears in multiple positions (field type, method return type, etc.), test ALL references, not just the first one encountered.
  - **Assuming the qualified name is always well-formed**: The qualified name of a local type could unexpectedly include a numeric prefix derived from its parent container's naming. Always validate that the first character of the qualified name is not a digit.
  - **Forgetting to compare across references**: Even if individual qualified names look plausible, they should be consistent (equal) across all references to the same type.

### Correct Example (what the test should look like)

```java
@Test
public void testLocalTypeQualifiedNameIsConsistentAndValid() {
    // Build a model containing a local type
    CtClass<?> localType = ...; // e.g., a class declared inside a method
    
    // Collect all CtTypeReferences pointing to this local type
    List<CtTypeReference<?>> refs = localType.getFactory().Type().getAllTypeReferencesTo(localType);
    
    assertFalse("There should be at least one type reference", refs.isEmpty());
    
    for (CtTypeReference<?> ref : refs) {
        String qName = ref.getQualifiedName();
        // The qualified name should not start with a digit
        assertFalse(
            "Qualified name starts with a number: " + qName,
            qName.matches("^[0-9].*")
        );
    }
    
    // All references should produce the same qualified name
    String firstQName = refs.get(0).getQualifiedName();
    for (CtTypeReference<?> ref : refs) {
        assertEquals(firstQName, ref.getQualifiedName());
    }
}
```

### Incorrect Example (would miss the bug)

```java
@Test
public void testLocalTypeSimpleName() {
    CtTypeReference<?> ref = getSomeReference();
    // WRONG: only checks simple name, not qualified name
    assertEquals("MyLocalClass", ref.getSimpleName());
    // This test would pass even if getQualifiedName() returns "1MyLocalClass"
}
```