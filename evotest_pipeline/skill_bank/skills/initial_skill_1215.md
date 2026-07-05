---
name: iso-date-time-parse-validation
description: When parsing date/time strings from protocol messages, the code must
  handle missing or null date fields gracefully. This skill teaches how to test that
  date-time parsing rejects invalid/missing date literals and returns null instead
  of throwing an uncaught exception.
code_tags:
- VALIDATION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# iso-date-time-parse-validation

## Instructions

# ISO Date-Time Parse Validation

## Instructions

- WHEN the code parses a date/time string from a protocol message (e.g., using `DateTime.parse()` with an ISO-like format)
- THEN the TG should write a test that passes a null date literal argument and verify the parsing method returns `null` without throwing an exception
- Additionally, test with a malformed date string (e.g., empty string, or non-date text) and verify the method either returns `null` or throws a controlled, declared exception — never an uncaught `IllegalArgumentException`
- The test should specifically call the decode method with a message that contains no date field (or null in the date position), and assert that no exception is thrown and the result is `null` for the timestamp

### Common pitfalls
- Testing only with valid date strings — this misses the null/missing-date case
- Assuming the date field will always be present in every protocol message
- Writing integration tests that mock or skip the date parsing call entirely

### Correct example (pseudocode)
```java
// WHEN the message contains no date field (null date literal)
// THEN decode should not throw and should return null position/time
@Test
public void testDecodeWithNullDate() throws Exception {
    OsmAndProtocolDecoder decoder = new OsmAndProtocolDecoder(...);
    // Create a message with a null date field
    Object msg = createMessageWithNullDate();
    assertDoesNotThrow(() -> decoder.decode(null, null, msg));
    Object result = decoder.decode(null, null, msg);
    // If result is a position, its timestamp should be null or default
    if (result instanceof Position) {
        assertNull(((Position) result).getFixTime());
    }
}
```

### Incorrect example (pseudocode)
```java
// BAD: Only testing with valid date — misses the null-date crash
@Test
public void testDecode() throws Exception {
    OsmAndProtocolDecoder decoder = new OsmAndProtocolDecoder(...);
    Object msg = createMessageWithValidDate();
    // This passes but gives false confidence — null date will crash
    Object result = decoder.decode(null, null, msg);
    assertNotNull(result);
}
```