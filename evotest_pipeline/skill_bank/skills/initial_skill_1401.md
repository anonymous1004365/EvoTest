---
name: response-filter-add-null-check
description: When a method adds an element to a lazily-initialized collection, tests
  must verify both that null elements are rejected and that the collection can accept
  valid elements after lazy initialization. Apply this skill when you see addResponseFilter-like
  patterns with null-checks on collection members.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- RESPONSE_FILTER_ADDITION
- COLLECTION_MUTATION
test_pattern: EXCEPTION_TEST
---

# response-filter-add-null-check

## Instructions

# Response Filter Null Check and Collection Mutation

## Instructions

- WHEN you encounter a method that adds an element to a lazily-initialized collection field (e.g., `addResponseFilter(IResponseFilter responseFilter)` which checks `if (responseFilters == null) { responseFilters = new ArrayList<>(3); }` before calling `responseFilters.add(responseFilter)`)
- THEN the TG MUST write a test that:
  1. Calls the `add*` method with a `null` argument and asserts that an appropriate exception is thrown (e.g., `IllegalArgumentException` with a message like "Argument 'responseFilter' may not be null").
  2. After the null call fails, calls the method again with a valid non-null argument and asserts that no exception is thrown — this validates that a failed null call does not corrupt the lazy initialization state.
  3. Verifies the collection contains the added element (e.g., `assertThat(settings.getResponseFilters(), hasItem(filter))`).
- Common pitfalls to avoid:
  - Testing only the null rejection without testing that a subsequent valid add succeeds (the null argument must not leave the lazy-initialized collection in a broken state).
  - Testing only the happy path (valid add) without testing null rejection.
  - Forgetting to call the getter (e.g., `getResponseFilters()`) to assert the element was actually stored.
  - Assuming the method returns `this` (fluent API) — check the actual return type and assert on it if it returns a value.

### Correct example
```java
@Test
void addResponseFilter_nullArgument_throwsException()
{
    RequestCycleSettings settings = new RequestCycleSettings();
    assertThrows(IllegalArgumentException.class, () -> settings.addResponseFilter(null));
    // Even after the exception, the lazily-initialized collection must work
    IResponseFilter filter = mock(IResponseFilter.class);
    settings.addResponseFilter(filter);
    assertThat(settings.getResponseFilters(), hasItem(filter));
}
```

### Incorrect example (missing the post-failure valid add)
```java
@Test
void addResponseFilter_nullArgument_throwsException()
{
    RequestCycleSettings settings = new RequestCycleSettings();
    assertThrows(IllegalArgumentException.class, () -> settings.addResponseFilter(null));
    // BUG: Does not verify that the method works after a null rejection.
    // The lazy initialization might be in a corrupted state.
}
```