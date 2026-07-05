---
name: flume-persistent-manager-lifecycle
description: When testing appender managers that use resource lifecycle patterns (start/stop/send),
  test that the manager correctly handles the sequence of operations — especially
  verifying that events sent after stop do not corrupt the internal state or leave
  resources unclosed. Apply when a manager wraps a transactional resource like a Flume
  client.
code_tags:
- RESOURCE_MANAGEMENT
- STATE_MUTATION
- VALIDATION
test_pattern: INTERACTION_TEST
---

# flume-persistent-manager-lifecycle

## Instructions

# Flume Persistent Manager Lifecycle Test Skill

## Instructions

- WHEN the TG encounters a test that checks sending events through a **FlumeAppender** (or similar appender) that uses a **FlumePersistentManager** (or similar manager) with `start()`, `stop()`, and event-sending methods
- THEN the TG should write a test that:
  1. Creates the appender with a valid configuration (e.g., with an agent string using the `FlumeAppender.createAppender(...)` factory method)
  2. Starts the appender explicitly via `appender.start()`
  3. Sends a log event via the appender (using `appender.append(logEvent)`)
  4. Stops the manager explicitly via `appender.stop()`
  5. Attempts to send another log event **after** stop
  6. Verifies that the **second send does not throw an exception** (the manager should gracefully ignore the event after stop)
- The key insight is that the manager should handle the `stopped` state gracefully — events sent after stop should be a no-op, not an **AppenderRuntimeException** or any other exception
- Include concrete constants: use `"test"` as the appender name, a single agent string like `"localhost:4141"`, and the built-in `FlumeEventFactory` via `FlumeEventFactory.getFactory()`
- Common pitfalls to avoid:
  - ❌ Testing only the happy path (start → send → receive) without testing the post-stop behavior
  - ❌ Assuming the manager throws an exception when sending after stop (the bug was that it threw an `AppenderRuntimeException` instead of silently ignoring)
  - ❌ Forgetting to use `appender.stop()` which is the proper way to stop the manager through the appender lifecycle
  - ❌ Using raw `FlumePersistentManager.getManager(...)` directly instead of going through the appender lifecycle

### Correct Example (tests the bug)

```java
@Test
public void testSingle() {
    final FlumeAppender appender = FlumeAppender.createAppender("test", null, null, "localhost:4141", null, null, null, null, null, null, null, FlumeEventFactory.getFactory(), null);
    appender.start();
    final LogEvent event = Log4jLogEvent.newBuilder().setLoggerName("test").setLevel(Level.INFO).setMessage(new SimpleMessage("Test")).build();
    appender.append(event);
    appender.stop();
    // This second append should NOT throw an exception — it should be a no-op
    appender.append(event);
}
```

### Incorrect Example (misses the bug)

```java
@Test
public void testSingle() {
    final FlumeAppender appender = FlumeAppender.createAppender("test", null, null, "localhost:4141", null, null, null, null, null, null, null, FlumeEventFactory.getFactory(), null);
    appender.start();
    final LogEvent event = Log4jLogEvent.newBuilder().setLoggerName("test").setLevel(Level.INFO).setMessage(new SimpleMessage("Test")).build();
    appender.append(event);
    // ❌ Missing the second append after stop — this test won't catch the bug
    appender.stop();
}
```