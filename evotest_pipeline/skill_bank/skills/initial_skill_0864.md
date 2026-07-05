---
name: ctquery-foreach-type-validation
description: When iterating over query results using forEach or similar methods, test
  that the iteration does not throw a ClassCastException due to internal state corruption
  in the query chain. This skill is used when a CtQuery has steps like map/select/filter
  that process mixed-type results.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- ARGUMENT_VALIDATION
test_pattern: EXCEPTION_TEST
---

# ctquery-foreach-type-validation

## Instructions

# CtQuery forEach Type Safety Validation

## Instructions

- WHEN the TG encounters code that iterates over a CtQuery using `forEach` or evaluates a `CtQuery` with `.list()` or `.first()` after applying steps such as `.map()`, `.select()`, or `.filter()`
- THEN the TG should write a test that:
  1. Creates a query that processes elements of different types (e.g., mixing `CtTypeReference` with `CtAnnotation`, or `CtType` with `String`)
  2. Applies a map/select step that may attempt to cast elements to a type they don't match
  3. Invokes `.forEach(...)` on the query result and asserts that no `ClassCastException` is thrown
- The test must specifically verify that the internal state of the query (e.g., step chain) does not become corrupt, causing a `ClassCastException` when iterating
- Common pitfalls:
  - Testing only with homogeneous types (all elements of the same type) — this fails to trigger the bug
  - Using `.list()` instead of `.forEach()` — the bug may only manifest during lazy iteration
  - Forgetting to apply `.map()` or `.select()` before the terminal operation — the corruption happens during step chaining
  - Assuming that if `.list()` works, `.forEach()` also works — they may use different code paths

### Correct example:
```java
// Given a factory that creates mixed elements
CtQuery query = factory.createQuery(...)
    .map((CtTypeReference ref) -> ref.getSimpleName()); // mixes String and CtTypeReference in state
query.forEach(result -> {
    // No ClassCastException should occur
});
```

### Incorrect example:
```java
// Only testing with list()
List<?> results = factory.createQuery(...).map(...).list(); // May pass but forEach still fails
```