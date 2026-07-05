---
name: template-parameter-type-validation
description: When validating method parameters that accept generic types like `Class<?>`, tests must cover both the expected subtype and the parent/interface type to catch gaps in type filtering logic.
code_tags: ['VALIDATION', 'STATE_MUTATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that validates or filters parameters by type (e.g., checking if a parameter `isAssignableFrom` some class, or filtering by `Class<?>`), and the parameters can include both concrete implementations and parent/interfaces of those implementations:
  - THEN the TG should write a **parametric test** that passes values of **multiple distinct types**: (1) a subtype/concrete implementation, and (2) a parent/supertype/interface of that implementation.
  - The test must verify that **only the expected types** are accepted and that unexpected parent types are **rejected** (or handled correctly).
  - For collection parameters (e.g., `List<Object>` containing mixed types), the test must verify that elements of unexpected types do **not** get processed/added, and that the collection's state remains consistent (e.g., size unchanged).

- WHEN testing type-based filtering logic where a collection is populated based on parameter type checks:
  - THEN the TG should test with a collection that contains **both** matching and non-matching types, and assert the **final state** of the collection (e.g., expected size, expected elements).

- Common pitfalls to avoid:
  - ❌ Testing only one parameter type (e.g., only a concrete `String` class) — this misses the bug where parent types (e.g., `CtTypeReference`) also pass the filter.
  - ❌ Only testing with `String` type parameters when the method accepts any `Class<?>` — string-like types may pass but other types (`CtTypeReference`, `Class<?>`) should be tested too.
  - ❌ Forgetting to verify the final size/state of collections after processing mixed-type inputs.

### Correct example (what the test should do):
```java
// Given a method that processes template parameters and populates a list:
void processParameter(List<String> results, Object param) {
    // should only handle String params, not CtTypeReference
}

// Test both types:
@Test
void testParameterTypeFiltering() {
    List<String> results = new ArrayList<>();
    processor.processParameter(results, "hello");            // should be accepted
    processor.processParameter(results, new CtTypeReference()); // should be REJECTED
    assertEquals(1, results.size());  // only String added
}
```

### Incorrect example (what misses the bug):
```java
// Only testing String type - misses bug where CtTypeReference gets through:
@Test
void testParameterTypeFiltering() {
    List<String> results = new ArrayList<>();
    processor.processParameter(results, "hello");
    assertEquals(1, results.size());  // passes but doesn't catch the bug
}
```