---
name: errorcode-unknown-type-handling
description: When testing ErrorCode enum conversion from an unknown or null error
  source type, the converter must handle unrecognized types gracefully without throwing
  an unexpected exception. This skill teaches how to test type conversion edge cases
  in enum-based error code mapping.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- TYPE_CONVERSION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# errorcode-unknown-type-handling

## Instructions

# ErrorCode Unknown Type Handling

## Instructions

- WHEN the TG encounters an `ErrorCode` enum (or similar enum-based error code mapping) that converts from a source object (e.g., a `Throwable`, `String`, or custom type) using a method like `from(ErrorSource)` or `convert(ErrorSource)`
- THEN the TG should **test the conversion behavior when the source type is unknown/unrecognized** (e.g., a custom class or null that does not match any expected ErrorCode value), and verify:
  - That the converter does NOT throw a `NullPointerException`, `IllegalArgumentException`, or `ClassCastException`
  - That it returns the expected fallback/default `ErrorCode` (e.g., `ErrorCode.OTHER` or `UNKNOWN`)
  - That it handles **null input** by returning the fallback or a safe default, not by crashing
- WHEN the converter internally calls methods on the source object (e.g., `source.getMessage()`, `source.getClass()`), the TG must ensure the test covers:
  - **Null source** — the converter should check for null before calling any methods on it
  - **Custom/unexpected source type** — the converter should gracefully fall back rather than fail
- Common pitfall: testing only the "happy path" with known error source types (e.g., `AxonServerException`, `StatusRuntimeException`) and missing the edge case where the source is of an unexpected type or null.

### Correct example (covers null + unknown type + expected fallback):
```java
@Test
void testConvertWithNullSource() {
    ErrorCode result = ErrorCode.from(null);
    assertEquals(ErrorCode.OTHER, result);
}

@Test
void testConvertWithUnknownSourceType() {
    class CustomException extends Throwable {}
    ErrorCode result = ErrorCode.from(new CustomException());
    assertEquals(ErrorCode.OTHER, result);
}
```

### Incorrect example (only happy path, misses null/unknown edge cases):
```java
@Test
void testConvertWithAxonServerException() {
    // Only tests known type — does not verify null or unknown type behavior
    ErrorCode result = ErrorCode.from(new AxonServerException("test"));
    // Missing: null source, custom exception type, etc.
}
```