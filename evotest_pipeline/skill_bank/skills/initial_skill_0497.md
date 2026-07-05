---
name: json-config-appenderref-level-validation
description: WHEN testing JSON configurations with AppenderRef arrays containing type-specific
  filtering (like level) for each appender, THEN verify JSON config parsing correctly
  processes AppenderRef arrays with multiple entries and respects per-appender level
  filtering, not just the logger-level. This skill applies to JSON configuration parsing
  where AppenderRef entries can have nested attributes like "level" that must be individually
  applied.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# json-config-appenderref-level-validation

## Instructions

# JSON Configuration AppenderRef Level Validation

## Instructions

- WHEN the TG encounters JSON configuration parsing code that processes `AppenderRef` entries with per-appender level attributes (like `"level": "trace"`, `"level": "error"`)
- THEN it should write a test that:
  1. Creates a JSON configuration with multiple appenders where each `AppenderRef` in an array has its own `level` attribute
  2. Uses a logger that logs events at various levels (trace, debug, info, warn, error, traceExit/traceEntry)
  3. Asserts that each appender receives only events at or above its configured per-appender level threshold
  4. Verifies the count of events each appender receives (e.g., LIST1 with `level: "trace"` receives all 6 events, LIST2 with `level: "error"` receives only 1 error event)
  5. Also tests the case where a single (non-array) `AppenderRef` object with nested filters (like `MarkerFilter`) is used alongside the array form

- Common pitfalls to avoid:
  - Testing only that the logger-level filtering works without testing per-appender level filtering
  - Assuming all JSON `AppenderRef` entries are parsed as arrays when they could also be parsed as single objects (the JSON format supports `"AppenderRef": {"ref": "LIST1", "level": "trace"}` as a single object OR `"AppenderRef": [{"ref": "LIST1"}, {"ref": "LIST2"}]` as an array)
  - Not verifying that events are actually delivered to appenders (checking event counts is critical — the bug caused 0 events to be delivered)
  - Assuming the bug is in the test infrastructure rather than in the JSON configuration parsing logic

### Example (Correct)

```java
// This test validates that JSON config properly handles AppenderRef arrays with per-appender level filtering
@Test
public void testAppenderRefLevelFiltering() {
    // Use JSON config with AppenderRef array having per-appender levels
    Logger logger = context.getLogger("org.apache.logging.log4j.test1");
    ListAppender traceAppender = context.getListAppender("LIST1").clear();
    ListAppender errorAppender = context.getListAppender("LIST2").clear();
    
    logger.traceEntry();       // LIST1=trace ✓, LIST2=error ✗
    logger.debug("debug");     // LIST1=trace ✓, LIST2=error ✗
    logger.error("error");     // LIST1=trace ✓, LIST2=error ✓
    logger.info("info");       // LIST1=trace ✓, LIST2=error ✗
    logger.warn("warn");       // LIST1=trace ✓, LIST2=error ✗
    logger.traceExit();        // LIST1=trace ✓, LIST2=error ✗
    
    assertThat(traceAppender.getEvents(), hasSize(6));
    assertThat(errorAppender.getEvents(), hasSize(1));
}
```

### Example (Incorrect)

```java
// WRONG: Only tests logger-level filtering without per-appender level checking
@Test
public void testLoggerLevel() {
    Logger logger = context.getLogger("org.apache.logging.log4j.test1");
    ListAppender appender = context.getListAppender("LIST1").clear();
    logger.error("test");
    assertThat(appender.getEvents(), hasSize(1));
    // This doesn't test per-appender level filtering at all
}
```