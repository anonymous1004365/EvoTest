---
name: pagination-native-query-exception
description: When validating method arguments for native SQL queries, ensure pagination
  is rejected with a precise exception (IllegalStateException with clear message)
  rather than a generic NullPointerException or IllegalArgumentException.
code_tags:
- VALIDATION
- EXCEPTION_HANDLING
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# pagination-native-query-exception

## Instructions

# Pagination Validation in Native Queries

## Instructions

WHEN the TG encounters a method that validates query arguments for Spring Data JPA native queries — specifically a method that determines whether pagination can be applied to a native query — THEN it should test that the validation throws a precise, informative exception with a clear message explaining why pagination is unsupported for native queries.

- WHEN testing the `JpaQueryLookupStrategy` class's method that attempts to create a repository query with pagination parameters for a native query
- THEN the test should verify that a precise exception (e.g., `IllegalStateException` with a message like "Native queries do not support pagination") is thrown, NOT a generic `NullPointerException` or `IllegalArgumentException` without a clear message
- The test should expect the specific exception class and verify the exception message contains domain-relevant terms (e.g., "Native", "pagination", "unsupported")

### Common Pitfalls
- Testing only the exception type without checking the message content — a generic `IllegalArgumentException` is insufficient
- Assuming all invalid parameters produce the same exception class without verifying message specificity
- Using `NullPointerException` as a catch-all for validation failures
- Not testing with the exact parameter combination that triggers the problem (native query + Pageable parameter)

### Example (Correct)
```java
@Test
void sholdThrowMorePreciseExceptionIfTryingToUsePaginationInNativeQueries() {
    assertThatExceptionOfType(IllegalStateException.class)
        .isThrownBy(() -> lookupStrategy.createQuery(...))
        .withMessageContaining("Native")
        .withMessageContaining("pagination");
}
```

### Example (Incorrect — does not catch the bug)
```java
@Test
void shouldFailWhenPaginationUsedWithNativeQuery() {
    // This passes even if a NullPointerException is thrown instead of IllegalStateException
    assertThrows(Exception.class, () -> lookupStrategy.createQuery(...));
}
```