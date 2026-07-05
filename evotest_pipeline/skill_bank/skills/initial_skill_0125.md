---
name: null-safe-logging-after-shutdown
description: When testing async loggers that can be used after shutdown, verify that
  calling logging methods after a shutdown operation does not throw a NullPointerException.
  The TG should test with both direct Logger.log() calls and lambda log() calls after
  calling shutdown() then awaitTermination() on the logger context.
code_tags:
- CONCURRENCY
- NULL_CHECK
- STATE_MANAGEMENT
test_pattern: STATE_TEST
---

# null-safe-logging-after-shutdown

## Instructions

# Null-Safe Logging After Shutdown

## Instructions

- WHEN the TG encounters an `AsyncLogger` or `AsyncLoggerConfig` that has a `shutdown()` method followed by an `awaitTermination()` method, and the logger is used after shutdown completes
- THEN the TG should write a state test that:
  1. Calls `ctx.shutdown()` (the context of the logger) to initiate shutdown
  2. Calls `ctx.awaitTermination(timeout, TimeUnit)` to wait for shutdown completion
  3. After shutdown completes, calls the logging method (e.g., `logger.info("...")`) on the async logger
  4. Verifies that calling the logging method after shutdown does NOT throw a `NullPointerException`
- Include in the test:
  - A call to `ctx.shutdown()` followed by `ctx.awaitTermination(1, TimeUnit.SECONDS)` before logging
  - At least one regular `logger.info("test")` call and optionally a lambda-based `logger.info("test {}", () -> "param")` call
  - Assert that the test completes without any exception (do NOT assert specific log output — just verify no NPE)
- Common pitfalls to avoid:
  - Testing only before shutdown or only during shutdown, not after shutdown has fully completed
  - Not calling `awaitTermination()` after `shutdown()` (shutdown is async and may not complete immediately)
  - Testing only `info()` but not other log levels like `warn()` or `error()`
  - Assuming the logger is null after shutdown — the test should verify the logger object is still usable, not that it returns a value
- Correct example test structure:
  ```java
  @Test
  public void testNoErrorIfLogAfterShutdown() throws Exception {
      final LoggerContext ctx = ...; // get the logger context
      final Logger logger = ctx.getLogger(AsyncLoggerUseAfterShutdownTest.class.getName());
      logger.info("before shutdown"); // verify logger works before
      ctx.shutdown();
      ctx.awaitTermination(1, TimeUnit.SECONDS); // ensure shutdown is complete
      logger.info("after shutdown"); // this should NOT throw NPE
  }
  ```
- Incorrect example (pitfall):
  ```java
  @Test
  public void testLogAfterShutdown() throws Exception {
      final LoggerContext ctx = ...;
      final Logger logger = ctx.getLogger(...);
      ctx.shutdown();
      // missing awaitTermination() — test is flaky as shutdown may not have completed yet
      logger.info("after shutdown"); // may or may not throw NPE depending on timing
  }
  ```