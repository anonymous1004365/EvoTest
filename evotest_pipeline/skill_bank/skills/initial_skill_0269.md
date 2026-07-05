---
name: wiretap-threadpool-executor-service-cleanup
description: When using WireTap with a custom thread pool or executor service, tests
  must verify that the processor correctly creates and manages the inner ExecutorService
  without triggering IndexOutOfBoundsException on collection accesses during service
  lifecycle.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- ARRAY_INDEX_ACCESS
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# wiretap-threadpool-executor-service-cleanup

## Instructions

# WireTap Processor ExecutorService Cleanup

## Instructions

- WHEN the TG encounters a test that sets up a WireTap endpoint with a custom thread pool (ExecutorService) via `wireTap("direct:foo").executorService(executorService)` or chain configuration, AND the test involves adding/removing exchange listeners or processors during `setUp()` or route initialization:
  - THEN the TG should verify that no `IndexOutOfBoundsException` is thrown when accessing internal processor lists or collections during route startup/shutdown.
  - Specifically, WHEN using a shared or custom executor service with WireTap, test that the processor does not trigger concurrent modification or index out-of-bounds access on its internal processor list when the executor service is reused or shut down.
  - Verify by running the route multiple times or in a setUp that starts and stops the camel context, ensuring that the wire tap's internal `createExecutorService` flow properly synchronizes or guards against empty/boundary conditions on collection accesses.
  - Common pitfalls: The TG might test only the happy path where WireTap works once, missing the case where the executor service lifecycle (create/cleanup) causes an `IndexOutOfBoundsException` inside `add/remove` processor or listener lists. Always test with at least 2 exchange submissions when using a custom executor service to force collection access patterns that can trigger the bug.
  - Example correct approach: Create a test that uses `.wireTap("direct:foo").executorService(myService)` and submits two or more exchanges to the route, asserting that no exception is thrown and all exchanges complete normally.
  - Example incorrect approach: Testing only with `.wireTap("direct:foo")` (default thread pool) or submitting only a single exchange, which would not expose the race/boundary condition.