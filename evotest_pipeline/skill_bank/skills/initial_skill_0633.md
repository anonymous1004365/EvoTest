---
name: protocol-decoder-null-safety
description: WHEN decoding binary GPS protocol messages with optional fields, THEN
  test with missing or null-position data to ensure the decoder handles null coordinates
  gracefully instead of crashing with NullPointerException. Apply this skill to any
  protocol decoder that parses byte buffers into position objects.
code_tags:
- NULL_CHECK
- TYPE_CONVERSION
- PARSING
test_pattern: EXCEPTION_TEST
---

# protocol-decoder-null-safety

## Instructions

# Protocol Decoder Null Safety

## Instructions

- WHEN the TG encounters a protocol decoder class that parses raw binary/string messages (e.g., a class extending `BaseProtocolDecoder`) and constructs a `Position` object
- THEN the TG MUST write a test that feeds an otherwise valid message that intentionally lacks some coordinate/position data (e.g., no latitude/longitude, or zero-length coordinate fields). The test MUST verify that the decoder does NOT throw a `NullPointerException` and instead either gracefully returns `null` or constructs a `Position` with default coordinate values.
- Include concrete examples: pass a byte buffer or string payload where critical fields like GPS fix status, latitude, or longitude are missing (e.g., all zeros for speed/coordinates, or an empty/corrupted coordinate field).
- Common pitfall: testing only with fully valid messages and assuming the decoder handles all edge cases. The decoder may crash with `NullPointerException` when it tries to call `.doubleValue()` or similar methods on a null result from coordinate parsing (e.g., when `Parser.next()` returns `null` for latitude/longitude tokens).
- The test should use JUnit's `assertDoesNotThrow` (or catch the exception and fail) to verify no exception is thrown, even when the decoded Position may be `null`.

**Correct example (catches the bug):**
```java
@Test
public void testDecodeWithMissingFields() {
    GoSafeProtocolDecoder decoder = new GoSafeProtocolDecoder(null);
    ByteBuf buf = Unpooled.copiedBuffer(Hex.decodeHex(
        "0000000000000000000000000000000000000000000000"));
    assertDoesNotThrow(() -> {
        Object result = decoder.decode(null, null, buf);
        // May return null, but must not throw
    });
}
```

**Incorrect example (misses the bug):**
```java
@Test
public void testDecodeWithValidMessage() {
    GoSafeProtocolDecoder decoder = new GoSafeProtocolDecoder(null);
    ByteBuf buf = Unpooled.copiedBuffer(Hex.decodeHex(
        "08290001035959905999ea0b000000000000000000000f0000"));
    Position position = (Position) decoder.decode(null, null, buf);
    assertNotNull(position);
    assertEquals(37.123, position.getLatitude(), 0.001);
}
```