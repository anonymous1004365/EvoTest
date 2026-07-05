---
name: async-logger-config-initialization-race
description: When testing async logger configurations that start logging before the
  configuration is fully initialized, the test must wait for the async event queue
  to drain before asserting results. This skill teaches how to use test rules that
  properly synchronize async configuration startup and shutdown.
code_tags:
- CONCURRENCY
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# async-logger-config-initialization-race

## Instructions

# Async Logger Config Initialization Race

## Instructions

- WHEN the TG encounters a test for async loggers (using `AsyncLoggerConfig`, `AsyncLogger`, or any logging that uses a separate thread/ring buffer to process log events asynchronously)
- THEN the test MUST ensure that the async configuration is fully initialized before logging, AND that all async events are fully processed before making assertions on appender state. Use a `@Rule` / `@ClassRule` `LoggerContextRule` that points to a test configuration XML file (e.g. `"AsyncLoggersWithAsyncAppenderTest.xml"`). The `Reconfigurable` context in the test rule handles both initialization and teardown properly.

- THEN the test MUST verify that the `ListAppender` (or any custom appender counting events) has received the expected number of events. Use `TestUtil.waitFor()` or `Thread.sleep(100)` to allow async event processing to complete before checking counts. Directly checking `listAppender.getEvents().size()` immediately after logging will fail in async configurations because the events may not have been dispatched yet.

- THEN the test should call `LoggerContextRule.getListAppender("ListAppenderName")` (or similar lookup) to get the appender reference, clear it before logging, log a known number of events (e.g., 2-3), wait for async processing, then assert the count is correct.

- Common pitfalls to avoid:
  - NOT waiting for async event queue to drain before asserting — this is the primary bug cause (the test expects events immediately after logging, but they are processed on a separate thread)
  - Using purely synchronous test setup for async logger configurations
  - Not clearing the appender between test runs, leading to stale events accumulating across test methods
  - Using the wrong XML configuration file that does not set up async logger configs properly
  - The test must use `@Test` with expected timeout or proper synchronization, not just rely on sleep timing

### Correct example:
```java
@Before
public void setUp() {
    listAppender = context.getListAppender("List").clear();
}

@Test
public void testLoggingWorks() {
    logger.info("First message");
    logger.info("Second message");
    // Wait for async events to be processed
    TestUtil.waitFor("List", 2000, () -> listAppender.getEvents().size() == 2);
    assertEquals(2, listAppender.getEvents().size());
}
```

### Incorrect example (will fail randomly for async configs):
```java
@Test
public void testLoggingWorks() {
    logger.info("First message");
    logger.info("Second message");
    // BUG: No wait — events may not have been dispatched yet
    assertEquals(2, listAppender.getEvents().size()); // FAILS: expected 2, got 0
}
```