---
name: protocol-decoder-date-timezone-validation
description: When writing tests for protocol decoders that parse timestamp packets,
  ensure both String-type and numeric-type timestamps are tested to verify timezone-offset
  logic doesn't break on edge-case dates like epoch. This skill helps catch bugs where
  date parsing mishandles timezone offsets for dates near epoch boundaries.
code_tags:
- BOUNDARY_CHECK
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-date-timezone-validation

## Instructions

# Protocol Decoder Timestamp & Timezone Edge-Case Testing

## Instructions

- WHEN the TG encounters a protocol decoder that parses timestamp/date fields from device packets — specifically methods that decode hex messages and convert timestamps into Date objects using timezone offsets — THEN it should write a parametric test that covers at least two distinct timestamp types: (1) a String-type timestamp parameter (e.g., the hex packet bytes representing a date-time like "0712041800" = 2007-12-04 18:00 UTC), and (2) a numeric/edge-case timestamp (e.g., epoch "0101010000" = 2001-01-01 00:00 UTC or "0000010000" = 2000-01-01 00:00 UTC). The test must verify that the decoded position's fixTime is non-null and corresponds to the correct date, confirming that timezone offset addition/subtraction does not produce a wrong date or null. On the buggy version, the edge-case near epoch boundary produces a Date in the wrong month or day due to timezone miscalculation when the timestamp string is parsed and then the offset is applied.

- WHEN the TG sees that the decoder code splits a timestamp string into date and time parts (e.g., `dateStr = timestamp.substring(0, 6)`, `timeStr = timestamp.substring(6)`) and applies a timezone offset (e.g., `Calendar.ZONE_OFFSET` or `TimeZone.getTimeZone`), THEN it should test with timestamps that are near epoch boundaries (e.g., years 2000 or 2001) in addition to "typical" timestamps (e.g., year 2007+). Common pitfalls include (a) only testing with String-type integer arguments without testing numeric-type arguments, (b) only testing with timestamps well after epoch where timezone offset doesn't cross a month/year boundary, (c) assuming the parsed date always matches the expected date without considering that timezone offset subtraction can push the result into the previous day/month/year.

- Include at least one correct example: a test that passes both a String parameter (e.g., "0712041800") and an int parameter (e.g., 7010100000) to the decode method, verifying fixTime is not null and matches the expected epoch millis. Include at least one incorrect example: a test that only uses the String parameter type without the int/numeric type, missing the timezone-offset bug on edge-case dates.

```java
// Correct: Parametric test covering both String and int timestamp types
@ParameterizedTest
@CsvSource({
    "0712041800, STRING, 2007-12-04T18:00:00Z",
    "0701010000, INT, 2007-01-01T00:00:00Z"
})
void testDecodeWithEdgeCaseTimestamps(String hexInput, String type, String expectedDate) {
    Gt02ProtocolDecoder decoder = new Gt02ProtocolDecoder(null);
    // ... set up channel, sender, session
    Object msg = decoder.decode(channel, sender, hexInput);
    assertNotNull(((Position) msg).getFixTime());
    // Verify fixTime matches expectedDate
}
```

```java
// Incorrect: Only tests String-type, misses timezone edge-case
@Test
void testDecode() {
    Gt02ProtocolDecoder decoder = new Gt02ProtocolDecoder(null);
    Object msg = decoder.decode(channel, sender, "0712041800");
    assertNotNull(((Position) msg).getFixTime());
    // Bug: does not test int/numeric-type timestamps near epoch
}
```