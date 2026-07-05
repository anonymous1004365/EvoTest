---
name: field-access-before-parent-initialization
description: When testing CtFieldAccess or similar field-access expressions that reference
  enclosing types, construct objects without initializing their parent container/nesting
  context to verify field-access printing works even when the parent reference or
  enclosing type holder is null. This catches NullPointerExceptions in pretty-printing
  code paths that dereference parent/owner references without null checks.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# field-access-before-parent-initialization

## Instructions

# Field Access Before Parent Initialization

## Instructions

- WHEN the TG encounters a class that accesses or prints field expressions referencing enclosing or outer types (e.g., CtFieldAccess with an `getVariable()` returning a CtTypeReference that has a `getPackage()` or `getDeclaringType()` chain), AND the pretty-printing or field-access resolution code may dereference the parent/owner reference:

  - THEN the TG should construct a test where:
    1. Create the field-access object (e.g., CtFieldAccess) WITHOUT initializing its parent/enclosing-type hierarchy (i.e., leave the parent reference `null`).
    2. Invoke the print/toString/output method on that field-access object.
    3. Verify no NullPointerException (or other unexpected exception) is thrown.
    4. Verify the output is meaningful (non-null, non-empty) even without parent initialization.

- Include concrete values/exceptions from the actual code:
  - If the field access has a `getFactory()` or `getParent()` that returns null, the test must cover that null case.
  - The specific exception to expect on the buggy version is `NullPointerException` when the print method tries to traverse the parent chain.

- Common pitfalls to avoid:
  - **Do NOT** set up the full parent/container hierarchy before calling the method under test — the bug is precisely that the code crashes when parent is NOT set.
  - **Do NOT** test only the "happy path" where all references are fully initialized.
  - **Do NOT** assume that because a parent reference is typically set during construction, it is always non-null at print time.

### Correct Example (catches the bug)

```java
@Test
public void testPrintCtFieldAccessWorkEvenWhenParentNotInitialized() {
    // Create a factory or builder
    CtFieldAccess<?> fieldAccess = factory.createFieldAccess();
    // Intentionally do NOT set parent/enclosing type — leave it null
    
    // This should NOT throw NullPointerException
    String result = fieldAccess.prettyPrint();
    assertNotNull(result);
    assertFalse(result.isEmpty());
}
```

### Incorrect Example (misses the bug)

```java
@Test
public void testPrintCtFieldAccessWithFullSetup() {
    CtFieldAccess<?> fieldAccess = factory.createFieldAccess();
    // Setting up the full parent hierarchy — this hides the bug
    CtType<?> parentType = factory.createType();
    fieldAccess.setParent(parentType);
    
    // This always passes because parent is non-null
    String result = fieldAccess.prettyPrint();
    assertNotNull(result);
}
```