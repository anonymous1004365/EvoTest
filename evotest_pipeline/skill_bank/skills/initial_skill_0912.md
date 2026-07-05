---
name: marker-propagation-in-log-methods
description: When a CountingLogger-like test helper tracks marker state set via setCurrentEvent,
  and the AbstractLogger log methods (e.g., error, debug, fatal) propagate markers
  via logIfEnabled/logMessageSafely, the TG should test that the marker passed to
  log() is the same as the marker delivered to the actual logging implementation.
  Apply this skill when testing marker-based logging with a custom Logger subclass
  that captures logged events.
code_tags:
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# marker-propagation-in-log-methods

## Instructions

# Marker Propagation in Log Methods

## Instructions

- WHEN the TG encounters logging methods (error, debug, warn, fatal, trace, info) that accept a Marker parameter, AND the Logger under test is a custom subclass (e.g., CountingLogger extending AbstractLogger) that captures log events via a mutable currentEvent state set by setCurrentEvent(LogEvent):
  - THEN the TG should create a test that:
    1. Creates a non-null Marker (e.g., `MarkerManager.getMarker("TEST")`)
    2. Calls the log method with that marker (e.g., `logger.error(MARKER, "Hello")`)
    3. After the call, asserts that the captured event's marker name or marker field matches the expected marker, NOT null
  - Specifically, the TG must verify that when a logging method receives a non-null Marker, the marker is faithfully propagated through all overloaded method variants (e.g., `logger.error(Marker, String)`, `logger.error(Marker, String, Throwable)`, `logger.error(Marker, Object)`, `logger.error(Marker, Object, Throwable)`, `logger.error(Marker, Message)`, etc.)
  - Common pitfalls to avoid:
    - Testing only without a Marker (null marker) — the bug is that non-null markers get dropped in some methods
    - Testing only one overload variant (e.g., only `logger.error(MARKER, "Hello")`) while missing other overloads like `logger.error(MARKER, simple)`, `logger.error(MARKER, obj)`, `logger.error(MARKER, pattern, p1, p2)`, etc.
    - Not verifying that the marker delivered to the underlying log implementation matches the marker passed at the call site
    - Assuming that if one overload propagates markers correctly, all overloads do

**Correct Example:**
```java
@Test
public void testMarkerPropagation() {
    final CountingLogger logger = new CountingLogger();
    logger.setCurrentLevel(Level.ERROR);
    Marker testMarker = MarkerManager.getMarker("TEST");
    
    // Test with Message parameter
    LogEvent event = new LogEvent("TEST", new SimpleMessage("Hello"), null);
    logger.setCurrentEvent(event);
    logger.error(testMarker, new SimpleMessage("Hello"));
    assertEquals("Marker should be preserved", "TEST", logger.getCurrentEvent().markerName);
    
    // Test with String parameter
    event = new LogEvent("TEST", new SimpleMessage("Hello"), null);
    logger.setCurrentEvent(event);
    logger.error(testMarker, "Hello");
    assertEquals("Marker should be preserved", "TEST", logger.getCurrentEvent().markerName);
}
```

**Incorrect Example (would miss the bug):**
```java
@Test
public void testError() {
    final CountingLogger logger = new CountingLogger();
    // Only tests without marker — would not catch the marker-dropping bug
    logger.error("Hello");
    // Only tests one overload — other overloads may still be broken
    logger.error(MARKER, "Hello");
    // Does not assert on the marker at all
}
```