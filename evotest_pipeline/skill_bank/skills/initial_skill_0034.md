---
name: type-reference-equals-nullpointer
description: When a class overrides equals() and compares its own type reference field
  with a parameter that may not be the same type, the TG should test with objects
  of different types to catch potential ClassCastException or NullPointerException.
  This applies specifically to CtTypeReference.equals() implementations that fail
  to guard against type mismatches.
code_tags:
- TYPE_REFERENCE_EQUALS
test_pattern: EXCEPTION_TEST
---

# type-reference-equals-nullpointer

## Instructions

# Type Reference equals() NullPointerException

## Instructions

WHEN the TG encounters an `equals()` method in a class that wraps or holds a `CtTypeReference` (or any similar wrapper/reference type), and that `equals()` method accesses fields or methods on the parameter without first checking that the parameter is an instance of the same class:

- THEN the TG should write tests that call `equals()` with:
  - A completely unrelated object type (e.g., `String`, `Integer`, `CtTypeReference` itself)
  - A `null` value
  - An object of a sibling/subtype that lacks the expected fields
- THEN ensure the test verifies that NO exception (NullPointerException, ClassCastException) is thrown when comparing with unrelated types — the method should safely return `false`
- THEN test that comparing two equal instances of the same class returns `true`
- THEN test that comparing two different instances of the same class returns `false`
- AVOID assuming the equals parameter is always of the same type — the TG must test cross-type safety explicitly

### Example (Correct Test)

```java
@Test
public void testEqualsWithDifferentTypes() {
    // Assume CtTypeReferenceImpl wraps a CtTypeReference
    CtTypeReferenceImpl ref1 = new CtTypeReferenceImpl(...);
    
    // Should not throw NullPointerException or ClassCastException
    assertFalse(ref1.equals("unrelated type"));
    assertFalse(ref1.equals(null));
    assertFalse(ref1.equals(Integer.valueOf(42)));
}
```

### Example (Incorrect Test — misses the bug)

```java
@Test
public void testEqualsIncomplete() {
    CtTypeReferenceImpl ref1 = new CtTypeReferenceImpl(...);
    CtTypeReferenceImpl ref2 = new CtTypeReferenceImpl(...);
    
    // Only tests same-type scenarios — does NOT catch the NPE bug
    assertEquals(ref1, ref2);
    assertNotEquals(ref1, new CtTypeReferenceImpl(...));
}
```

### Common Pitfalls
- Testing only same-type comparison — the bug only manifests when `equals()` is called with an object of a different type
- Forgetting to test `equals(null)` — this is another common crash scenario for unguarded equals() methods
- Assuming the `equals()` contract is correctly implemented just because same-type comparisons work
- Missing the combination of type-check + field access: the buggy code casts without `instanceof` check first, then accesses fields that don't exist on the passed type