---
name: template-parameter-type-safety
description: When code validates template parameters or type arguments, the TG should
  test with both valid matching types and mismatched types to ensure type safety.
  This skill applies to methods that accept Class, CtTypeReference, or similar type
  descriptors and use them for lookup or comparison.
code_tags:
- TYPE_CONVERSION
- VALIDATION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# template-parameter-type-safety

## Instructions

# Template Parameter Type Safety

## Instructions

**WHEN** the code under test:
1. Accepts a type parameter (e.g., `Class<?>`, `CtTypeReference<?>`, `String`, or similar type descriptor) used to look up, validate, or operate on template/program elements
2. Performs type-based comparisons, conversions, or lookups (e.g., `equals()`, `isSubtypeOf()`, `getDeclaringClass()`, `@Target`, annotation processing)

**THEN** the TG should write a test that:
1. **Calls the method with a type that matches** — verify normal operation succeeds (no exception)
2. **Calls the method with a type that does NOT match** — verify the operation either:
   - Returns a sensible default/empty result (e.g., empty collection, null, -1)
   - Throws an appropriate exception (e.g., `IllegalArgumentException`, `NullPointerException`, `ClassNotFoundException`)
3. **Includes null type parameter** — verify the method handles `null` gracefully without throwing an unexpected exception
4. **Verifies the behavior matches the documented contract** — e.g., if the method says "returns the matching element or throws", test both branches

**Common pitfalls to avoid:**
- Testing only with the matching/expected type (the "happy path") — this misses validation failures with mismatched types
- Assuming type parameters are always used for reflection only — they may be compared using `.equals()` or used as map keys, so mismatched types may silently fail
- Forgetting that type parameters might be compared by name (String) vs by identity (Class object) — test both scenarios
- Not testing with `null` — many type validation methods crash with NPE on null input when they should either reject gracefully or the NPE should be documented

**Example (correct):**
```java
// Test that a valid type works
assertDoesNotThrow(() -> {
    CtTypeReference<?> result = processor.processType(String.class);
    assertNotNull(result);
});

// Test that a mismatched type returns null or throws
assertThrows(IllegalArgumentException.class, () -> {
    processor.processType(Integer.class); // or some other incompatible type
});

// Test null handling  
assertThrows(NullPointerException.class, () -> {
    processor.processType(null);
});
```

**Example (incorrect — only happy path, misses the bug):**
```java
// Only tests with String — never discovers the bug with other types
CtTypeReference<?> result = processor.processType(String.class);
assertEquals("java.lang.String", result.getQualifiedName());
```