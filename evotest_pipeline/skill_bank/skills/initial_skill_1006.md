---
name: missing-root-logger-appender-inheritance
description: When a root logger is absent/missing, the configuration may incorrectly
  inherit appenders from the root to other loggers, leading to unexpected appender
  counts. Use this skill when testing configuration with a missing root logger and
  verifying that appenders are not leaked across loggers.
code_tags:
- LOGGER_LEVEL_INHERITANCE
- STATE_MUTATION
test_pattern: STATE_TEST
---

# missing-root-logger-appender-inheritance

## Instructions

# Missing Root Logger Appender Inheritance

## Instructions

- WHEN the TG encounters configuration code where a root logger may be missing (not explicitly configured) and a default root logger is provided by the framework
- THEN the TG should test that when a non-root logger (e.g. `LoggerConfig` for a specific name like "sample") has its own appenders, those appenders are NOT inherited from or shared with the root logger.
  - Create a concrete configuration (e.g. using `ConfigurationFactory`, `Configuration`, or `LoggerContext`) where no root logger is explicitly defined.
  - Add a `LoggerConfig` for a specific logger name (e.g. "sample") with one or more appenders (e.g. using `ListAppender`, `FileAppender`, or `MockAppender`).
  - Retrieve the appenders of that specific logger via `loggerConfig.getAppenders()` and verify the count is as expected (e.g. `hasSize(1)` when one appender was added).
  - Also test the root logger: retrieve `rootLogger.getAppenders()` and verify its size — it should be empty (0) when no appenders were configured for it.
  - Expect that on the buggy version, the non-root logger's `getAppenders()` may incorrectly return a map that includes the root logger's appenders (causing an unexpectedly large size), while on the fixed version, `getAppenders()` returns only the appenders directly configured on that logger.

- Common pitfalls:
  - Testing only the root logger without also testing a non-root logger; the bug manifests in non-root loggers inheriting appenders they shouldn't.
  - Assuming that because a default root logger was created, all loggers will have the expected appender set — some loggers may unexpectedly gain extra appenders.
  - Not checking both the specific logger and the root logger; always verify appender counts on the logger under test AND on the root logger separately.

- Example correct approach:

```java
// Correct test: verifies appender count on a specific logger when root is missing
LoggerConfig sample = config.getLoggers().get("sample");
Map<String, Appender> sampleAppenders = sample.getAppenders();
assertThat("The sample logger should only have one appender", sampleAppenders, hasSize(1));

LoggerConfig root = config.getRootLogger();
Map<String, Appender> rootAppenders = root.getAppenders();
assertThat("The root logger should have zero appenders", rootAppenders, hasSize(0));
```

- Example incorrect approach:

```java
// WRONG: only checks root logger, may pass even when bug is present
LoggerConfig root = config.getRootLogger();
assertThat(root.getAppenders(), hasSize(0));  // This could pass on both buggy and fixed

// WRONG: doesn't check the specific logger's appender count
// The bug makes sample.getAppenders() return size > expected
```