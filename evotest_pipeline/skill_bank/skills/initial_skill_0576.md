---
name: creator-template-parameter-type-validation
description: When discovering creator/injectable value methods via reflection, the
  TG should test that both String type names and CtTypeReference type parameters are
  correctly accepted and do not cause duplicate entries or exceptions during method
  registration.
code_tags:
- TYPE_CONVERSION
- STATE_MUTATION
- CREATOR_TEMPLATE_PARAM_TYPE
test_pattern: PARAMETRIC_TEST
---

# creator-template-parameter-type-validation

## Instructions

# Creator Template Parameter Type Validation

## Instructions

- WHEN the TG encounters code that registers a creator method or injectable value method via reflection (e.g., using APIs like `addInjectableValueMethod`, `addParamIfNotPresent`, or similar methods that accept a template parameter for the type)
- THEN the TG should write parametric-style tests that pass **both** `String` type values and `CtTypeReference` type values as template parameters to exercise the method registration logic
  - Specifically: if the method has a type parameter `<T>` and an overloaded parameter (one that accepts `String` and another that accepts `CtTypeReference`), test with both
  - Verify that calling the method with a `String` type does NOT throw a `ClassCastException` or cause duplicate entries due to incorrect type matching
  - Verify that calling the method with both types produces the same single registration (not duplicates)

- WHEN the code under test caches or stores registrations keyed by type (e.g., using a `Map<Object, ...>`, `Multimap`, or similar structure) where the key could be either a `String` or a `CtTypeReference`
- THEN the TG should test that:
  - A `String` key and a `CtTypeReference` key that represent the same type do NOT result in duplicate entries
  - The `equals()`/`hashCode()` contract works correctly across these different key types
  - Adding a method with a `String` type parameter and then querying by the same `String` type finds the method correctly

- Common pitfalls:
  - Testing only `String` type parameters when the production code also accepts `CtTypeReference` (or vice versa)
  - Assuming that type parameters are always the same type in production
  - Not checking for duplicate entries when the same type is registered with different parameter type representations
  - Using only `assertEquals(expected, actual)` without also checking collection sizes or absence of duplicates

### Correct Example
```java
// Test that both String and CtTypeReference types work without duplicates
CreatorCollector collector = new CreatorCollector();
// Register with String type
Method m1 = ...; // creator method with String template param
collector.addInjectableValueMethod(m1);
// Register with CtTypeReference type representing same type
Method m2 = ...; // creator method with CtTypeReference template param
collector.addInjectableValueMethod(m2);
// Assert no exception was thrown
// Assert only one entry exists for the same type (not duplicate)
```

### Incorrect Example (too narrow)
```java
// BAD: Only tests one type of parameter
CreatorCollector collector = new CreatorCollector();
Method m = ...; // only uses String type
collector.addInjectableValueMethod(m);
// Misses the CtTypeReference case entirely
```