---
name: type-reference-equals-with-null-proxy
description: WHEN testing CtTypeReference equality, THEN test that equals() and hashCode()
  are consistent even when some fields are null and others are populated with proxy
  objects. This skill catches bugs where accessing proxy fields during equality comparison
  modifies internal state, breaking hashCode consistency.
code_tags:
- TYPE_REFERENCE_EQUALS
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# type-reference-equals-with-null-proxy

## Instructions

# Type Reference Equality with Null/Proxy Fields

## Instructions

- WHEN the TG encounters a class whose `equals()` or `hashCode()` method accesses fields that could be proxy templates (e.g., a `CtTypeReference` with fields like `actualClass`, `actualTypeArguments`, `package`, `declaringType`, `simpleName`)
- THEN it should create an object where some fields are `null` and then call `hashCode()` followed by `equals()` on a second object, verifying that `hashCode()` returns the same value after `equals()` was called as it did before (i.e., the hash code is stable and not mutated by the equals comparison)
- Specifically, the test should:
  1. Create two `CtTypeReference` instances representing the same type (e.g., both for `String`)
  2. Leave one field as `null` on one instance (e.g., `actualClass = null`) while the other instance has it populated (e.g., `actualClass = String.class`) — the equals should still return `false`
  3. On the instance with the null field, call `hashCode()` before and after calling `equals()` on it — assert that the hash code is the same
  4. Verify that the type reference with the null field can be added to a `HashSet` or used as a `HashMap` key without throwing `NullPointerException` or silently failing
- Common pitfalls to avoid:
  - **Do NOT** test only with fully-populated type references — the bug only manifests when some fields are null
  - **Do NOT** forget to test `hashCode()` stability before and after `equals()` — the bug is that `equals()` triggers lazy computation of proxy fields, mutating internal state
  - **Do NOT** assume that `equals()` either works or throws an exception — the bug may manifest as silent state corruption (inconsistent hash codes)
  - **Do NOT** test only String types — also test with `CtTypeReference` objects that have generic type arguments or are parameterized

## Example

### Correct Test Pattern
```java
// Test that hashCode is stable when equals triggers proxy field access
CtTypeReference<String> ref1 = factory.Type().createReference(String.class);
CtTypeReference<String> ref2 = factory.Type().createReference(String.class);
// Set a field to null on ref2 to simulate incomplete proxy resolution
ref2.setActualClass(null);

int hashBefore = ref2.hashCode();
// This call to equals may trigger lazy proxy field computation
boolean equal = ref2.equals(ref1);
int hashAfter = ref2.hashCode();

// The hash code MUST be stable
assertEquals("hashCode must be stable after equals()", hashBefore, hashAfter);

// If the types are equal, both should return true; if not, false
// The key assertion is hash code stability regardless
assertNotEquals("hashCode should differ when fields differ", 
    ref1.hashCode(), ref2.hashCode());
```

### Incorrect Test Pattern (would miss the bug)
```java
// BAD: only tests fully-populated references
CtTypeReference<String> ref1 = ...;
CtTypeReference<String> ref2 = ...;
assertEquals(ref1, ref2);
assertEquals(ref1.hashCode(), ref2.hashCode());
// Missing: no test with null fields, no hash-stability check
```

### Concrete Example from Spoon
```java
// Given the Spoon CtTypeReference bug with proxy fields:
// - actualClass can be null (lazy proxy)
// - equals() accesses actualClass via getActualClass() which resolves proxy
// - hashCode() also accesses actualClass
// The bug: equals() changes internal state (resolves proxy) so that
// subsequent hashCode() returns a different value

@Test
public void testTypeReferenceHashCodeStability() {
    CtTypeReference<String> ref1 = factory.Type().createReference(String.class);
    // Simulate a state where actualClass is null but other fields match
    CtTypeReference<String> ref2 = factory.Type().createReference(String.class);
    ref2.setActualClass(null);
    
    int hash1 = ref2.hashCode();
    ref2.equals(ref1);
    int hash2 = ref2.hashCode();
    
    assertEquals("hashCode changed after equals() call", hash1, hash2);
}
```