---
name: concurrent-schema-validation-safety
description: When a validator endpoint has useSharedSchema=false (or equivalent non-shared
  schema mode), concurrent validation of multiple messages using the same validator
  instance can cause Schema creation race conditions. This skill teaches how to test
  that concurrent validation with non-shared schemas does not throw exceptions.
code_tags:
- TYPE_CONVERSION
- NULL_CHECK
- VALIDATION
- UNSYNCHRONIZED_SCHEMA_CREATION
test_pattern: PERFORMANCE_TEST
---

# concurrent-schema-validation-safety

## Instructions

# Concurrent Schema Validation Safety

## Instructions

- WHEN the TG encounters a validator endpoint (e.g., `ValidatorEndpoint` or `JsonValidatorEndpoint`) that has a `useSharedSchema` option (or equivalent flag controlling whether a `Schema` object is shared across exchanges), and the default value is `true`:
  - THEN the TG MUST write a test that sends multiple messages concurrently through the validator when `useSharedSchema=false`.
  - The test MUST use at least 2 concurrent threads sending messages through the same validator route endpoint.
  - The test MUST verify that no exception (especially `NullPointerException` or `IllegalStateException`) is thrown during concurrent validation.
  - The specific route should be: `from("direct:start").to("validator:path/to/schema.xsd?useSharedSchema=false")`.
  - Use `MockEndpoint` to collect results and assert that all messages were processed successfully (no failures, no exceptions).

- WHEN the TG is writing a concurrent test for schema validation:
  - THEN the TG MUST use `ExecutorService` with at least 2 threads and submit multiple messages in parallel.
  - Use `template.asyncSendBody()` or `template.sendBody()` from multiple threads.
  - Use `assertTrue("Should not fail", ...)` or check `mockEndpoint.assertIsSatisfied()` without exception.
  - A common pitfall is testing only sequential (single-threaded) validation, which does not expose the race condition in `createSchema()` when schemas are not shared.

- Common pitfalls to avoid:
  - ❌ Testing only with `useSharedSchema=true` (default) — the bug only manifests when `useSharedSchema=false`.
  - ❌ Sending messages one at a time (sequential) — the race condition requires concurrent access to `createSchema()`.
  - ❌ Using a single-threaded executor — no concurrency means no race condition.
  - ❌ Forgetting to catch or assert that no exceptions bubble up from the concurrent sends.

- Example of a correct test:

```java
public void testConcurrentUseNotASharedSchema() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMessageCount(10);

    ExecutorService executor = Executors.newFixedThreadPool(5);
    for (int i = 0; i < 10; i++) {
        final int index = i;
        executor.submit(() -> {
            template.sendBody("direct:start", 
                "<mail><subject>Hey</subject><body>Hello World!</body></mail>");
            return null;
        });
    }

    assertTrue("Should not fail", mock.await(10, TimeUnit.SECONDS));
    mock.assertIsSatisfied();
    executor.shutdownNow();
}
```

- Example of an INCORRECT test (would NOT catch the bug):

```java
// WRONG: Sequential sends don't trigger the race condition
public void testValidationNotShared() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMessageCount(5);

    for (int i = 0; i < 5; i++) {
        template.sendBody("direct:start", 
            "<mail><subject>Hey</subject><body>Hello World!</body></mail>");
    }

    mock.assertIsSatisfied();
}
```