---
name: template-parameter-type-validation
description: When a method receives a collection (e.g., Set, List) of mixed-type parameters (e.g., Strings, CtTypeReferences) for template/proxy resolution, TG should test with both type categories to ensure the method handles heterogeneous types correctly without crashing or returning incorrect results.
code_tags: ['STATE_MUTATION', 'VALIDATION', 'TYPE_CONVERSION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that accepts a collection of parameter values for template processing (e.g., processing proxy template parameters from a `Set`), and the parameters could be of different Java types (e.g., `String` and `CtTypeReference`):
  - THEN the TG should write a test that passes a collection containing at least **one parameter of type `String`** and **one parameter of type `CtTypeReference`** (or whichever concrete types the buggy code mixes).
  - THEN the test should verify that the method correctly processes **all** parameter types and does not throw an exception, return null, or silently skip certain types.
  - THEN the TG should also test with **duplicate keys** across different types (e.g., same string value as both `String` and `CtTypeReference`) to expose incorrect deduplication logic in the collection.
- Common pitfalls:
  - Testing only with `String` type parameters, which works fine but misses the bug when `CtTypeReference` or other types are involved.
  - Assuming that `Set.contains()` or `Set.add()` correctly deduplicates elements of different types — they don't, because `String` and `CtTypeReference` have different `hashCode()`/`equals()` implementations unless explicitly handled.
  - Not iterating over all elements in the collection to verify they were all processed correctly.

### Correct Example
```java
// GOOD: Tests with mixed types to catch heterogeneous parameter handling
Set<Object> params = new HashSet<>();
params.add("myParam");           // String type
params.add(someTypeReference);   // CtTypeReference type
// Call the method and verify both params are processed
assertNotNull(result);
assertTrue(result.contains("myParam"));
assertTrue(result.contains(someTypeReference));
```

### Incorrect Example
```java
// BAD: Tests only with String type parameters — misses the bug entirely
Set<Object> params = new HashSet<>();
params.add("param1");
params.add("param2");
// This passes even on buggy code, giving false confidence
```