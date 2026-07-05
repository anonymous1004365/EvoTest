---
name: creator-collector-non-duplicate-validation
description: When validating creator parameters in Jackson's CreatorCollector, both
  the method parameter type and the literal value type must be checked for duplicates.
  Only checking String type misses duplicates involving non-String types like CtTypeReference.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# creator-collector-non-duplicate-validation

## Instructions

# Creator Collector Non-Duplicate Validation

## Instructions

- WHEN the TG encounters code in `CreatorCollector` that validates or filters creator parameters (constructors, factory methods) using `SettableBeanProperty[]` arrays, and the code checks for duplicates (non-duplication) by comparing parameter properties
- THEN the TG must verify that the duplicate-check logic handles **all parameter types**, not just `String`-typed parameters. The bug occurred because the validation only handled `String` type parameters. The TG should test by providing parameters with **non-String** types (e.g., `CtTypeReference` or custom object types) that have equal values to ensure the duplicate detection catches them as well.
- Include a parametric test that:
  1. Creates a `SettableBeanProperty` array with two properties having the **same name** but different types (one `String` type, the other a non-String type like `CtTypeReference` with equal value)
  2. Verifies that calling the validation method (e.g., `verifyNonDup` or similar) correctly identifies **both** as duplicates
  3. Expects the buggy version to **miss the non-String duplicate** (no exception thrown) while the fixed version should throw `IllegalArgumentException` for both
- Common pitfalls to avoid:
  - ❌ **Testing only with String-type parameters** — this misses the bug entirely
  - ❌ **Assuming type equality comparison** — the bug is that the code directly checks `param.getName()` for equality, missing non-String parameters
  - ❌ **Not testing duplicate detection with mixed types** (one String, one non-String) — the bug only manifests with non-String parameter values
  - ❌ **Testing only identical type parameters** (both String or both CtTypeReference) — the bug is about missing non-String *types* specifically

### Example (Correct Approach)

```java
// Correct: Tests with a non-String type parameter
@Test
public void testVerifyNonDupWithNonStringType() {
    CreatorCollector collector = new CreatorCollector(...);
    
    // Create properties with same name, one String type, one CtTypeReference type
    SettableBeanProperty prop1 = new SomeProperty("field1", String.class, ...);
    SettableBeanProperty prop2 = new SomeProperty("field1", CtTypeReference.class, ...);
    
    SettableBeanProperty[] properties = new SettableBeanProperty[] { prop1, prop2 };
    
    // This should throw IllegalArgumentException on the fixed version
    // Buggy version would NOT throw, silently accepting the duplicate
    assertThrows(IllegalArgumentException.class, () -> {
        collector.someMethod(properties);
    });
}
```

### Example (Incorrect Approach — misses the bug)

```java
// ❌ Wrong: Only tests String-type parameters
@Test
public void testVerifyNonDupWithStringType() {
    CreatorCollector collector = new CreatorCollector(...);
    
    SettableBeanProperty prop1 = new SomeProperty("field1", String.class, "value1");
    SettableBeanProperty prop2 = new SomeProperty("field1", String.class, "value2");
    
    SettableBeanProperty[] properties = new SettableBeanProperty[] { prop1, prop2 };
    
    assertThrows(IllegalArgumentException.class, () -> {
        collector.someMethod(properties);
    });
    // This passes on BOTH buggy and fixed versions — doesn't catch the bug!
}
```