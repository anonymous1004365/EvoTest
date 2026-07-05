---
name: alternative-protocol-decoding-with-special-message-types
description: When a protocol decoder handles alternative message types (e.g., special
  IDs or frame formats) that use a different decoding path than the primary format,
  the TG should write tests exercising those special branches to catch incorrect frame
  parsing, buffer boundary detection, or silent failures.
code_tags:
- VALIDATION
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-with-special-message-types

## Instructions

# Alternative Protocol Decoding with Special Message Types

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., `EelinkProtocolDecoder`) that processes multiple message types (e.g., distinguished by a message ID, type byte, or frame flag)
- THEN the TG should identify ALL decoding branches/alternative paths and create parameterized tests that exercise each branch with representative payloads
  - Include tests for the "primary" message format AND any "alternative" formats (e.g., special type IDs, extended frames, heartbeats, acknowledgment frames)
  - Test with edge cases: minimum/maximum payload length, payloads at buffer boundary, payloads with unexpected but valid field values
  - Verify correct frame boundary detection: the decoder should not consume extra bytes beyond the current frame
  - For the buggy version, the test should expect an incorrect decoded value, an exception (e.g., `IndexOutOfBoundsException`, `IllegalArgumentException`, `BufferUnderflowException`), or silently wrong output (e.g., null/zero fields where non-null/non-zero expected)

- Common pitfalls:
  - Testing only the "happy path" primary message type and missing the alternative decoding path entirely
  - Testing payloads that are too short or too long incorrectly — verify buffer lengths match the specific message type's specification
  - Not testing multiple frames concatenated in a single buffer (tests should send a buffer that contains one full frame of the alternative type)
  - Assuming all message types have the same field structure (e.g., same number of bytes for length, type, or body)

### Correct example (what to do):
```java
// Parameterized test covering multiple message types
@ParameterizedTest
@CsvSource({
    // Format: hexPayload, expectedId, expectedValue
    "6767010C000100010003001122334455667788, 1, 0x1122334455667788",   // primary type
    "676702050000000200030015AABB, 2, 0xAABB",                         // special alternative type (shorter body)
    "6767FF0300000003000400000000, 3, 0"                               // edge case: zero value
})
void testDecodeAlternativeTypes(String hexPayload, int expectedId, int expectedValue) {
    ByteBuf buf = Unpooled.copiedBuffer(Hex.decodeHex(hexPayload));
    Channel channel = mock(Channel.class);
    Object result = decoder.decode(channel, null, buf);
    assertNotNull(result);
    assertInstanceOf(MyMessage.class, result);
    assertEquals(expectedId, ((MyMessage) result).getId());
}
```

### Incorrect example (what NOT to do):
```java
// Tests only the primary message type — misses alternative decoding path
@Test
void testDecodeOnlyPrimary() {
    String hex = "6767010C000100010003001122334455667788";
    ByteBuf buf = Unpooled.copiedBuffer(Hex.decodeHex(hex));
    Object result = decoder.decode(channel, null, buf);
    // This passes on primary type but doesn't catch bugs in alternative branches
}
```