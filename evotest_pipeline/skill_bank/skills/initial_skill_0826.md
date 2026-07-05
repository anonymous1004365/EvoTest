---
name: decoding-protocol-technology-type-validation
description: WHEN testing protocol decoders that handle byte-to-data conversion in
  different technologies (e.g., L100 protocol parsing), THEN tests must verify both
  normal decoding and edge cases like type mismatches, null/empty inputs, and partially
  valid data sequences to catch silent failures. Common pitfalls include only testing
  valid input or assuming the decoder framework handles all type conversions correctly.
code_tags:
- NULL_CHECK
- VALIDATION
- EXCEPTION_HANDLING
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# decoding-protocol-technology-type-validation

## Instructions

# Decoding Protocol Technology Type Validation

## Instructions

- WHEN the TG encounters a protocol decoder that uses a framework with a `decode` method taking technology-specific typed parameters (e.g., `Channel`, `SocketAddress`, and a protocol message type like `Object`)
- THEN the TG must write parametric tests that verify:
  1. **Correct protocol message parsing**: Pass a valid byte buffer/message for the specific protocol technology and verify the resulting decoded POJO fields are correctly populated.
  2. **Type conversion robustness**: Test with different message variants that exercise type conversion paths (e.g., converting bytes to int, long, string, boolean) and verify no silent fallback to default values — assert expected exception or correct decoded value.
  3. **Invalid/malformed data**: Test with null, empty, or partially truncated protocol messages to ensure the decoder does not proceed with partial/invalid data (expect an appropriate exception or a clear error indicator).
  4. **Technology-specific edge cases**: If the protocol uses a technology like JT/T 808, GPS byte parsing, or a proprietary binary format, test boundary values (e.g., max/min latitude/longitude, timestamps at epoch boundaries).

- WHEN writing the test, the TG must NOT assume the decoded object will be null on failure — some decoders return partially-filled POJOs instead. Verify the decoded object's fields directly.

- Common pitfalls to avoid:
  - **Only testing valid/successful decoding paths** — this misses silent data corruption bugs.
  - **Assuming the decoder returns `null` on invalid input** — the decoder may return a partially populated object with default/null fields.
  - **Not testing the specific technology's data format quirks** (e.g., byte order, encoding, checksum).
  - **Using a single test case** — use parameterized tests to cover normal, boundary, and invalid cases.

## Example Correct Approach

```java
// Parameterized test covering normal + invalid cases for the L100 protocol decoder
@ParameterizedTest
@CsvSource({
    // Normal valid message (hex string)
    "+RESP:GL100,869606049650713,,,230626,093052,12345678A,2231.5432,N,11354.8765,E,0.00,0,0,0,0,0,00000000,1,1,1,1,1,1#",
    // Invalid: missing fields
    "+RESP:GL100,869606049650713,,,230626,093052#",
    // Invalid: wrong technology prefix
    "+RESP:GL200,1234#"
})
void testDecode(String hexMessage) {
    L100ProtocolDecoder decoder = new L100ProtocolDecoder();
    Channel channel = mock(Channel.class);
    SocketAddress remoteAddress = mock(SocketAddress.class);
    ByteBuf buf = Unpooled.wrappedBuffer(hexMessage.getBytes(StandardCharsets.US_ASCII));
    Object result = decoder.decode(channel, remoteAddress, buf);
    
    // For valid input, verify decoded fields
    if (hexMessage.startsWith("+RESP:GL100,") && hexMessage.contains("2231.5432")) {
        assertNotNull(result);
        assertTrue(result instanceof Position);
        Position position = (Position) result;
        assertNotNull(position.getLatitude()); // Verify latitude was parsed
        assertEquals(22.52572, position.getLatitude(), 0.00001);
        assertNotNull(position.getLongitude());
        assertEquals(113.91460833, position.getLongitude(), 0.00001);
    } else {
        // For invalid input, ensure no partial data is returned as valid
        assertNull(result);
    }
}
```

## Example Incorrect Approach

```java
// WRONG: Only tests a single valid decoding path
@Test
void testDecodeOnlyValid() {
    L100ProtocolDecoder decoder = new L100ProtocolDecoder();
    // Only send valid data — misses null/invalid/truncated cases
    String msg = "+RESP:GL100,869606049650713,,,230626,093052,12345678A,2231.5432,N,11354.8765,E,0.00,0,0,0,0,0,00000000,1,1,1,1,1,1#";
    ByteBuf buf = Unpooled.wrappedBuffer(msg.getBytes(StandardCharsets.US_ASCII));
    Object result = decoder.decode(mock(Channel.class), mock(SocketAddress.class), buf);
    // Does not verify the decoded object's actual fields — just checks non-null
    assertNotNull(result);
}

// WRONG: Assumes null return on invalid input without verification
@Test
void testInvalidMessage() {
    L100ProtocolDecoder decoder = new L100ProtocolDecoder();
    ByteBuf buf = Unpooled.wrappedBuffer("garbage".getBytes());
    Object result = decoder.decode(mock(Channel.class), mock(SocketAddress.class), buf);
    // May incorrectly fail — decoder might return partially populated object
    assertNull(result);
}
```