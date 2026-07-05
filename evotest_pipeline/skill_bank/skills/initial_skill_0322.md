---
name: custom-slf4j-marker-checked-cast
description: When testing a logging bridge that wraps custom Marker implementations,
  ensure that custom SLF4J Marker objects that implement org.slf4j.Marker but are
  not instances of the bridge's own Marker wrapper class are handled without ClassCastException.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# custom-slf4j-marker-checked-cast

## Instructions

# Custom SLF4J Marker Type Cast Safety

## Instructions

- WHEN the TG encounters a logging bridge implementation (e.g., `Log4jLogger`) that converts SLF4J `Marker` objects to the bridge's internal `Marker` type via a direct cast on method parameters like `org.slf4j.Marker`:
  - THEN the TG should test that custom SLF4J `Marker` implementations (classes that implement `org.slf4j.Marker` but are NOT instances of the bridge's own `Marker` wrapper class, e.g. `org.apache.logging.slf4j.Log4jMarker`) can be passed to logging methods (e.g., `info(Marker, String)`, `warn(Marker, String, Throwable)`, `error(Marker, String)`, etc.) without throwing a `ClassCastException`.
  - Specifically, mark any SLF4J logging bridge method that takes a `Marker` parameter and casts it to the bridge's internal `Marker` type as a ClassCastException risk.
  - The test should:
    1. Create a custom class that implements `org.slf4j.Marker` (e.g., `CustomFlatMarker`) — a simple implementation that extends nothing from the bridge's own Marker hierarchy.
    2. Pass an instance of this custom Marker to each logging method accepting `Marker`.
    3. Expect that no `ClassCastException` is thrown — the bridge should handle arbitrary `Marker` implementations gracefully.
  - Additionally, verify that the custom Marker's attributes (e.g., `getName()`) are preserved correctly in the logged output.
  - Common pitfalls to avoid:
    - Testing only with the bridge's own `Marker` type (e.g., only `Log4jMarker`) — this masks the bug since the cast succeeds.
    - Not testing all overloaded logging methods (e.g., missing `error(Marker, String, Throwable)` or `warn(Marker, String)`).
    - Assuming that `Marker` parameter types are treated uniformly across all logging levels — test at least `info`, `warn`, `error` variants.
    - Not providing a proper `getName()` implementation in the custom Marker — some bridges rely on this to create their wrapper; without it, the test might fail for unrelated reasons.

### Correct test example (Java/JUnit):
```java
class CustomFlatMarker implements Marker {
    private final String name;
    public CustomFlatMarker(String name) { this.name = name; }
    @Override public String getName() { return name; }
    @Override public void add(Marker reference) {}
    @Override public boolean remove(Marker reference) { return false; }
    @Override public boolean hasChildren() { return false; }
    @Override public boolean hasReferences() { return false; }
    @Override public Iterator<Marker> iterator() { return Collections.emptyIterator(); }
    @Override public boolean contains(Marker other) { return false; }
    @Override public boolean contains(String name) { return false; }
}

@Test
public void supportsCustomSLF4JMarkers() {
    Logger logger = LoggerFactory.getLogger("TestLogger");
    Marker customMarker = new CustomFlatMarker("TEST");
    assertDoesNotThrow(() -> logger.info(customMarker, "Test message"));
    assertDoesNotThrow(() -> logger.warn(customMarker, "Test warn"));
    assertDoesNotThrow(() -> logger.error(customMarker, "Test error"));
}
```

### Incorrect test example (too narrow):
```java
// Tests only the bridge's own Marker type — won't catch the ClassCastException bug
Marker log4jMarker = new Log4jMarker(MarkerManager.getMarker("TEST"));
logger.info(log4jMarker, "message");  // Always works, no bug caught
```