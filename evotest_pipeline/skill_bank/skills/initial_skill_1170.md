---
name: hunterpro-protocol-position-parsing
description: When decoding HunterPro GPS protocol messages, the position fields (latitude,
  longitude, speed, course, altitude) may be parsed at incorrect buffer offsets or
  with wrong type handling. This skill ensures tests cover all position fields with
  correct byte-level parsing.
code_tags:
- PROTOCOL_POSITION_PARSING
- NETTY_CHANNEL_HANDLER_DECODING
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# hunterpro-protocol-position-parsing

## Instructions

# HunterPro Protocol Position Parsing

## Instructions

- WHEN the TG encounters a Netty channel handler decoder class (e.g., `HunterProProtocolDecoder`) that parses binary protocol messages into positions
- THEN it should write a parametric test that feeds known-good binary byte sequences and verifies each decoded position field:
  - `latitude` and `longitude` must be parsed as raw integer values (not scaled/divided) from specific buffer offsets
  - `speed` must be parsed from the correct offset (not confused with a similar field like course/heading)
  - `course` (heading) must be parsed from its own dedicated offset
  - `altitude` must be present when the protocol includes it, and its offset must be correct
- Use `org.traccar.model.Position` assertions to check each field independently
- WHEN writing the test input bytes, use `ByteBuf` (io.netty.buffer.Unpooled) to construct the raw protocol message with the exact byte layout the protocol specifies
- THEN assert that all decoded `Position` fields match expected values; a mismatch in any single field (especially swapped fields) indicates a regression
- Common pitfalls to avoid:
  - Testing only one field (e.g., latitude) — the bug may be in a less obvious field like altitude or course
  - Assuming field order in the buffer matches an arbitrary documentation order — verify each field's actual byte offset
  - Using generic integer assertions without checking the actual expected value for each field
  - Forgetting to test with byte values that would distinguish swapped fields (e.g., speed=10 vs course=10 are ambiguous if both are 10 — use distinct values like speed=50 vs course=180)

### Correct Example (what to do):
```java
// Test that all position fields are parsed at correct offsets
ByteBuf buf = Unpooled.buffer();
buf.writeByte(0xAB); // start marker
buf.writeBytes(...); // IMEI, etc.
buf.writeIntLE(expectedLatitude);   // latitude at offset X
buf.writeIntLE(expectedLongitude);  // longitude at offset Y
buf.writeShortLE(expectedSpeed);    // speed at offset Z
buf.writeShortLE(expectedCourse);   // course at offset W
buf.writeShortLE(expectedAltitude); // altitude at offset V
// ... rest of message

Position position = decoder.decode(null, null, buf);
assertEquals(expectedLatitude, position.getLatitude(), 0);
assertEquals(expectedLongitude, position.getLongitude(), 0);
assertEquals(expectedSpeed, position.getSpeed(), 0);
assertEquals(expectedCourse, position.getCourse(), 0);
assertEquals(expectedAltitude, position.getAltitude(), 0);
```

### Incorrect Example (what to avoid):
```java
// WRONG: Only checks latitude, misses other fields that could be swapped
ByteBuf buf = Unpooled.buffer();
buf.writeIntLE(12345); // latitude
// ... rest of message

Position position = decoder.decode(null, null, buf);
assertEquals(12345, position.getLatitude(), 0);
// No assertions on speed, course, altitude — misses the actual bug
```