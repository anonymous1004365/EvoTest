---
name: filter-for-each-cast-safety
description: When a collection filter method adds elements to a result list and then
  calls forEach on it, the test should verify that adding elements of different types
  (e.g., CtTypeReference vs String) doesn't cause ClassCastException when iterating,
  and that null elements are handled safely.
code_tags:
- COLLECTION_ITERATION
- TYPE_CONVERSION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# filter-for-each-cast-safety

## Instructions

# Filter forEach Cast Safety

## Instructions

- WHEN test has a filter method that collects elements into a results list (e.g., `List<Object> result = ...`) and later iterates over that list using `forEach`
- THEN the test should exercise the filter by populating the input with at least one element of a type that IS valid (e.g., a `CtTypeReference`) and also check that the list can be iterated without throwing a `ClassCastException`.
- WHEN elements added to the results list are `CtTypeReference<?>` objects, but the filter's method also accepts and passes through `String` inputs, verify that calling `forEach` on the collected list does NOT assume a specific type for all elements.
- Include a test that calls the filter method, populates its parameters with both types (e.g., `CtTypeReference` and `String`), then calls `forEach` with a lambda (e.g., a simple counting or identity expression) that can handle any `Object`.
- Common pitfalls to avoid:
  - Testing only with a single `String` type parameter, missing the cast issue when `CtTypeReference` elements are present.
  - Not calling `forEach` on the returned list at all, missing the runtime `ClassCastException`.
  - Assuming the filter returns a typed collection like `List<CtTypeReference>` when it actually returns a raw `List`.
  - Using a typed lambda (e.g., `CtTypeReference t -> ...`) that would itself cause a `ClassCastException` when encountering mismatched types.

### Incorrect (misses the bug):
```java
// Only tests with String parameters — no ClassCastException occurs
Filter filter = new SomeFilter();
filter.addInput("someString");
filter.addInput("anotherString");
Object result = filter.filter(); // returns a list
// Never iterates the list — bug not triggered
```

### Correct (catches the bug):
```java
// Tests with both CtTypeReference and String — triggers ClassCastException on forEach
CtTypeReference<?> ref = factory.Type().createReference(SomeClass.class);
Filter filter = new SomeFilter();
filter.addInput(ref);
filter.addInput("someString");
List<?> result = filter.filter();
// This forEach throws ClassCastException on buggy code because the filter
// collected CtTypeReference elements but the internal iteration casts to String
assertThrows(ClassCastException.class, () -> result.forEach(o -> {}));
```