---
name: protocol-decoder-timestamp-validation
description: When writing tests for protocol decoders that parse timestamp/date/time
  fields from network messages, test that the decoder correctly handles and validates
  each timestamp format. This skill catches bugs where timestamps are parsed without
  proper format validation, potentially accepting invalid/malformed date-time strings.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-timestamp-validation

## Instructions

# Protocol Decoder Timestamp Validation

## Instructions

- WHEN the TG encounters a protocol decoder that parses timestamp/date/time fields from a network protocol message buffer (e.g., using `DateBuilder`, `DateFormat`, `SimpleDateFormat`, or custom date parsing logic)
- THEN it should write a test that sends a protocol message with a **malformed or invalid timestamp field** (e.g., wrong date format, extra digits, truncated date, non-numeric characters, out-of-range month/day values)
- Proper timestamp parsing should either throw an exception (e.g., `IllegalArgumentException`, `ParseException`) or reject the message/return null for the timestamp field
- On the buggy version, the test should expect the decoder to **fail** (throw an exception or produce incorrect output) — demonstrating that the fix now properly validates the timestamp

**What to verify:**
- Verify that invalid date/time strings do NOT silently produce incorrect Date objects
- Verify that the decoder's response contains the expected number of positions/events (0 or the correct count with null timestamps), OR that an appropriate exception is thrown

**Common pitfalls to avoid:**
- Testing only the "happy path" with well-formed timestamps (the buggy code may work for valid inputs but silently accept invalid ones)
- Forgetting to test boundary cases like empty strings, extra characters appended to valid dates, or wrong date format patterns
- Assuming all timestamp formats accept the same malformed inputs — test each format individually
- Writing tests that only verify the decoder doesn't crash, without checking that the timestamp value is correctly parsed or rejected

**Correct example (catching the bug):**
```java
// WHEN sending a message with an invalid timestamp format
// THEN the decoder should NOT silently produce a valid Date
@Test
public void testDecodeWithInvalidTimestamp() throws Exception {
    CguardProtocolDecoder decoder = new CguardProtocolDecoder(null);
    // Example: message with malformed datetime field where timestamp is "2022-13-01 00:00:00" (month 13 is invalid)
    String invalidTimestampMsg = "..."; // binary/hex message with bad timestamp
    assertThrows(SomeException.class, () -> {
        decoder.decode(null, null, invalidTimestampMsg);
    });
    // OR if the decoder gracefully handles it:
    // Object result = decoder.decode(null, null, invalidTimestampMsg);
    // assertNull(((Position) result).getFixTime());
}
```

**Incorrect example (not catching the bug):**
```java
// WRONG: Only testing valid timestamps
@Test
public void testDecodeValidTimestamp() throws Exception {
    CguardProtocolDecoder decoder = new CguardProtocolDecoder(null);
    // Only testing with perfectly valid timestamp — won't catch validation bugs
    String validMsg = "..."; // binary/hex message with valid timestamp
    Object result = decoder.decode(null, null, validMsg);
    assertNotNull(result);
}
```