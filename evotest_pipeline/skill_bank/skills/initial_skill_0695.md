---
name: logger-serializability-round-trip
description: When testing serializable logger implementations, verify that serialization
  round-trip works correctly and that the deserialized object is properly functional.
  This is especially important for logger wrappers that hold transient references
  to underlying loggers and need custom readObject/writeObject methods to restore
  state.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
- SERIALIZATION
- INHERITANCE_HIERARCHY
test_pattern: INTERACTION_TEST
---

# logger-serializability-round-trip

## Instructions

# Logger Serializability Round-Trip Testing

## Instructions

- WHEN the TG encounters a class that implements `Serializable` and holds `transient` references to an underlying logger object (e.g., `Log4jLogger` with `transient ExtendedLogger logger`, `transient EventDataConverter converter`)
- THEN it should test that the object survives a complete serialization round-trip (write to `ObjectOutputStream`, read from `ObjectInputStream`) and verify both the original and deserialized object work correctly:
  1. Create a serializable logger instance (e.g., `Log4jLogger` wrapping an `ExtendedLogger`)
  2. After deserialization, verify the restored object is not null and is an instance of the expected class
  3. Verify the reference to the underlying `ExtendedLogger` is properly restored by calling logging methods (e.g., `logger.info("test")`)

- This bug specifically occurs when:
  - The class `Log4jLogger implements LocationAwareLogger, Serializable`
  - The class `SLF4JLogger extends AbstractLogger` where `AbstractLogger implements ExtendedLogger, Serializable` — but `SLF4JLogger` does NOT implement `Serializable` itself (it inherits it through `AbstractLogger`)
  - The `SLF4JLogger` holds a `final org.slf4j.Logger logger` field that is NOT transient but is a non-Serializable SLF4J logger implementation (`org.slf4j.impl.SLF4JLogger`), causing `NotSerializableException`

- Common pitfalls to avoid:
  - **Testing only through `Log4jLogger`**: The fix may involve `SLF4JLogger` which is obtained through `LoggerFactory.getLogger(...)`. The test must cast the result to `(Serializable)` and attempt round-trip serialization.
  - **Not testing round-trip at all**: Simply calling `writeObject()` without verifying `readObject()` can miss deserialization failures.
  - **Verifying only the top-level class**: The test must verify that ALL non-transient fields in the serialization chain are themselves serializable. In this bug, `SLF4JLogger` inherits `Serializable` from `AbstractLogger` but holds an `org.slf4j.Logger` that might not be serializable.
  - **Using mocks instead of realistic instances**: The test should use real logger objects (obtained from `LoggerFactory.getLogger(...)`) that exercise the actual serialization path.

- Example of a **correct** test:
```java
@Test
public void testLoggerSerialization() throws Exception {
    Logger logger = LoggerFactory.getLogger("LoggerTest");
    // Cast to Serializable to verify it's actually serializable
    assertThat((Serializable) logger, serializesRoundTrip());
}
```

- Example of an **incorrect** test that would miss the bug:
```java
@Test
public void testLoggerSerialization() {
    Logger logger = LoggerFactory.getLogger("LoggerTest");
    // Only checks instanceof, doesn't actually serialize
    assertTrue(logger instanceof Serializable);
}
```

- To properly test for this bug, use a custom round-trip approach if `serializesRoundTrip()` matcher is unavailable:
```java
@Test
public void testLoggerRoundTrip() throws Exception {
    Logger logger = LoggerFactory.getLogger("LoggerTest");
    ByteArrayOutputStream bos = new ByteArrayOutputStream();
    ObjectOutputStream oos = new ObjectOutputStream(bos);
    oos.writeObject(logger);
    oos.close();
    
    ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
    ObjectInputStream ois = new ObjectInputStream(bis);
    Logger deserialized = (Logger) ois.readObject();
    ois.close();
    
    assertNotNull(deserialized);
    assertTrue(deserialized instanceof Logger);
    // Verify deserialized logger is functional
    deserialized.info("test");
}
```