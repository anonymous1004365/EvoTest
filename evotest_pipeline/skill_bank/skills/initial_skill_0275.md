---
name: parallel-multicast-exception-wrapping
description: When testing multicast processors with parallel processing and stopOnException,
  the TG should verify that exceptions are properly unwrapped from ExecutionException
  rather than being wrapped. This skill applies to parallel fork-join patterns where
  exceptions lose their original type.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- STRING_MANIPULATION
- EXCEPTION_HANDLING
- CONCURRENCY
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# parallel-multicast-exception-wrapping

## Instructions

# Parallel Multicast Exception Wrapping

## Instructions

- WHEN the TG encounters a multicast processor using `.parallelProcessing()` combined with `.stopOnException()` (such as `MulticastProcessor` with parallel processing enabled)
- THEN it should test that when one processor in the multicast throws an exception (e.g., `IllegalArgumentException`), the exception thrown by the route is NOT wrapped in a `java.util.concurrent.ExecutionException`. Instead, it should be the original exception type or wrapped in a `CamelExchangeException` — never `ExecutionException`. The test must:
  - Use `@Test(expected = CamelExchangeException.class)` or similar on the specific exception type
  - Set up routes like: `from("direct:start").multicast().parallelProcessing().stopOnException().to("mock:a", "direct:sub")`
  - Have one sub-route throw a specific exception (e.g., `throw new IllegalArgumentException("Forced")`)
  - Assert that the test fails with the correct exception type (NOT `ExecutionException`)
- Common pitfalls to avoid:
  - Testing only serial (non-parallel) multicast processing — the bug is specific to parallel processing
  - Not enabling `stopOnException()` — the bug occurs when this flag is combined with parallel processing
  - Using `@Test(expected = Exception.class)` which is too broad and would mask the difference between `ExecutionException` vs `CamelExchangeException`
  - Testing only the happy path (no failures) — the test MUST trigger an exception in one of the parallel branches