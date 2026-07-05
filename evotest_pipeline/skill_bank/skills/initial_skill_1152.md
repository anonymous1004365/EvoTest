---
name: alternative-decoding-path-validation
description: ''
code_tags:
- TYPE_CONVERSION
- VALIDATION
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: PARAMETRIC_TEST
---

# alternative-decoding-path-validation

## Instructions

# Alternative Decoding Path Validation

## Instructions

### WHEN you encounter a protocol decoder with multiple decoding paths (e.g., a primary path using `ServerMessage` wrapper and an alternative path decoding raw frames directly)
- **Identify the conditions** that select each path (e.g., whether the message is wrapped in a `ServerMessage` envelope, or a specific attribute/property is present/absent).
- **Construct a test input** that deliberately FAILS the primary-path condition so the alternative path is executed. For example, if the decoder first checks `message instanceof ServerMessage` or checks for a `ServerMessage` attribute, send a message WITHOUT the wrapping — e.g., a raw hex byte array or raw string.
- **Verify that the alternative path produces the correct decoded result** (e.g., a specific `Position` object with known lat/lon/time/other fields). The test should call the decoder's `decode` method with a `Channel` or `SocketAddress` and the raw message payload.
- **Expect a specific exception on the buggy version** if the alternative path has a type conversion bug (e.g., `ClassCastException`, `NumberFormatException`, `IllegalArgumentException`). On the fixed version, the same input should decode successfully.

### Common pitfalls to avoid
- **Testing only the primary path**: This is the most common mistake. If the primary path condition is always met in your tests (e.g., you always wrap in `ServerMessage`), the alternative path is never exercised and bugs in it remain hidden.
- **Assuming `String` type parameters are sufficient**: If the alternative path expects `ByteBuf` or `byte[]`, do not test only with `String` inputs. Match the exact expected parameter type for the alternative code branch.
- **Missing edge-case type mismatches**: Pay special attention to type casting in the alternative path — if the decoder casts to a specific type (e.g., `String` vs `byte[]` vs `CtTypeReference`), test with the type that triggers that cast, not just the common type.

### Correct approach
```java
// Example: If decoder has a primary path for ServerMessage-wrapped frames
// and an alternative path for raw frames (byte[]), test BOTH:

@Test
public void testDecodeAlternativePath() throws Exception {
    TelicProtocolDecoder decoder = new TelicProtocolDecoder(null);
    // Raw byte input that triggers the alternative decoding path
    // (no ServerMessage wrapping)
    ByteBuf buf = Unpooled.wrappedBuffer(hexStringToByteArray("...raw frame hex..."));
    Position position = (Position) decoder.decode(null, null, buf);
    assertNotNull(position);
    assertEquals(expectedLat, position.getLatitude(), 0.0001);
    assertEquals(expectedLon, position.getLongitude(), 0.0001);
}
```

### Incorrect approach (missing the bug)
```java
// BAD: Only tests the primary path (wrapped in ServerMessage)
@Test
public void testDecodePrimaryPath() throws Exception {
    TelicProtocolDecoder decoder = new TelicProtocolDecoder(null);
    // Always sends a ServerMessage-wrapped frame — alternative path never tested
    ServerMessage msg = new ServerMessage("...");
    Position position = (Position) decoder.decode(null, null, msg);
    // Bug in alternative path remains hidden
}
```