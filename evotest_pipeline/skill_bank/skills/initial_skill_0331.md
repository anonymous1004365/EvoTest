---
name: outputstream-flush-on-end-of-batch
description: When testing appenders that use OutputStreamManager with deferred flushing
  (immediateFlush=false), verify that output is written at end of batch. This skill
  guides tests for end-of-batch flushing behavior in logging appenders like FileAppender,
  XmlFileAppender, and RandomAccessFileAppender.
code_tags:
- RESOURCE_MANAGEMENT
- STATE_MUTATION
test_pattern: STATE_TEST
---

# outputstream-flush-on-end-of-batch

## Instructions

# OutputStream Flush on End of Batch

## Instructions

- WHEN the TG encounters a logging appender class (e.g., `FileAppender`, `XmlFileAppender`, `RandomAccessFileAppender`) configured with `immediateFlush="false"` and an `AsyncRoot` logger
- THEN the TG should write a STATE_TEST that:
  1. Configures the appender with `immediateFlush="false"` (via a configuration XML file or programmatic config)
  2. Logs a message using an `AsyncLogger` or `AsyncRoot` logger
  3. Calls `LoggerContexts.stop(loggerContext)` to properly shut down the context and flush pending events — this is crucial because the bug is that events are not flushed on end of batch
  4. Reads the output file and asserts that the logged message was indeed written to the file
  5. Verifies the file contains the expected message content (e.g., using `assertTrue(content.contains(...))` or a line-by-line check)

- WHEN the message logged is a simple string like `"line1"`
- THEN the test should read the output file and verify the string appears in the file content
- WHEN calling `LoggerContexts.stop(loggerContext)` is the mechanism to trigger flush
- THEN the test MUST call it before reading the file, otherwise the file may be empty or incomplete

- Common pitfalls to avoid:
  - **Using an `AsyncRoot` without shutting down the context** — the test must call `LoggerContexts.stop(ctx)` to trigger batch end processing; simply closing the appender is not sufficient
  - **Testing with `immediateFlush="true"`** — the bug only manifests when `immediateFlush="false"`, as batch events are not individually flushed
  - **Testing synchronously** — the bug is specific to asynchronous logging (end-of-batch semantics); tests must use `AsyncRoot` or `AsyncLogger` to trigger the batch processing path
  - **Asserting the file exists but not its content** — verify that the expected message text is actually in the file, not just that the file was created

### Correct example:
```java
@Test
public void testFlushAtEndOfBatch() throws Exception {
    final LoggerContext ctx = LoggerContext.getContext(false);
    final Configuration config = ctx.getConfiguration();
    // ... configure File appender with immediateFlush=false ...
    final Logger logger = ctx.getLogger(getClass().getName());
    logger.info("line1");
    CoreLoggerContexts.stop(ctx);  // triggers flush at end of batch
    final File file = new File("target", "test.log");
    final String content = new String(Files.readAllBytes(file.toPath()));
    assertTrue("File should contain the logged message", content.contains("line1"));
}
```

### Incorrect example (missing flush trigger):
```java
@Test
public void testFlushAtEndOfBatch_WRONG() throws Exception {
    final LoggerContext ctx = LoggerContext.getContext(false);
    final Configuration config = ctx.getConfiguration();
    final Logger logger = ctx.getLogger(getClass().getName());
    logger.info("line1");
    // BUG: no ctx.stop() call — file may be empty
    final File file = new File("target", "test.log");
    final String content = new String(Files.readAllBytes(file.toPath()));
    assertTrue("File should contain the logged message", content.contains("line1"));
    // ^^^ This assertion will likely fail because events were never flushed
}
```