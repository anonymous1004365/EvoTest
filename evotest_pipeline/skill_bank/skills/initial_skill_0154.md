---
name: telic-fuel-report-timestamp-validation
description: When decoding fuel report messages where a timestamp field may be missing
  (null or empty), verify the decoder handles this case correctly by checking the
  trigger test's device timestamp behavior and ensuring no NullPointerException or
  incorrect mock setup occurs.
code_tags:
- VALIDATION
- NULL_CHECK
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# telic-fuel-report-timestamp-validation

## Instructions

# Telic Fuel Report Timestamp Validation

## Instructions

- WHEN the TG encounters a protocol decoder (e.g., `TelicProtocolDecoder`) that processes a `fuelReport` or similar sub-message containing a timestamp field (e.g., a `Date` parsed from a string, possibly via `SimpleDateFormat`),
- AND the timestamp value could be null, empty, or malformed (e.g., an empty string `""` or a non-date token) in the input data,
- THEN the TG should write a test that:
  1. Constructs a message where the timestamp field is missing/empty/null (e.g., `""` instead of a valid date string).
  2. Calls the decode method with that message.
  3. Asserts that the decoder **does not throw an exception** (i.e., it gracefully skips or handles the missing timestamp).
  4. Alternatively, if the decoder is supposed to reject such input, assert that a specific, documented exception (e.g., `IllegalArgumentException`) is thrown — NOT a `NullPointerException`.
- Common pitfalls:
  - Testing only with fully valid messages, missing the empty/null timestamp edge case.
  - Writing a test that expects `NullPointerException` (indicating a bug) instead of a graceful handled result.
  - Mocking the timestamp parsing in a way that silently returns a valid date even when input is empty.
  - Not testing both the fuel-report-specific path and the main decode path.

### ✅ Correct Test Approach

```java
@Test
public void testDecodeFuelReportMissingTimestamp() throws Exception {
    TelicProtocolDecoder decoder = new TelicProtocolDecoder();
    // Build a fuel report message with an empty timestamp field
    String msg = "...";  // e.g., "*XX,KEY,123456789012345,,12.34,56.78#"
    assertDoesNotThrow(() -> decoder.decode(null, null, msg));
    // Optionally verify that the timestamp in the result is null/zero
}
```

### ❌ Incorrect Test Approach

```java
@Test
public void testDecodeFuelReport() throws Exception {
    TelicProtocolDecoder decoder = new TelicProtocolDecoder();
    // Only tests a fully-valid message; missing timestamp case is untested
    String msg = "...";  // always has a valid date
    Position position = decoder.decode(null, null, msg);
    Assert.assertNotNull(position);
}
```