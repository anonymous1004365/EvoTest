---
name: protocol-alternative-decoding-path
description: When a protocol decoder has multiple alternative decoding paths (e.g.,
  based on message prefix or format), test each path separately to ensure frame decoding
  works for all message types. This skill helps catch bugs where one decoding path
  fails silently but the test only covers the other path.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
- NULL_CHECK
test_pattern: INTERACTION_TEST
---

# protocol-alternative-decoding-path

## Instructions

# Protocol Alternative Decoding Path Testing

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., `YwtProtocolDecoder`) that uses conditional logic to choose between multiple decoding paths (e.g., `if`/`else if` branches based on message prefix characters, message length, or other format indicators)
- THEN the TG should write separate test cases (individual test methods) that exercise **each** alternative decoding path with distinct input messages that trigger each branch. Each test should decode a realistic message for that specific path and verify that no exception is thrown during decoding.
- Include test messages that exercise the "edge" or "alternative" path — not just the most common one. For example, if a decoder switches between different parsing strategies based on the first character of the message (e.g., `0x10` vs `0x11` prefix), provide test inputs for both.
- The test should call `decode()` with a `ChannelHandlerContext` (possibly mocked) and a `String` or byte-array message, then verify the decoded result is non-null and contains expected fields (e.g., device ID, position data, status).
- Common pitfall: Testing only the "happy path" (most common message format) while the alternative path contains a bug (e.g., null reference, missing protocol byte handling, incorrect offset). Always test all branches.

✅ **Correct** (tests both paths with different message formats):
```java
@Test
public void testDecodeAlternativePath() throws Exception {
    YwtProtocolDecoder decoder = new YwtProtocolDecoder(new Protocol("ywt"));
    Channel channel = EmbeddedChannelFactory.build(decoder);
    
    // Alternative path message
    String altMsg = "*XX,123456789012345,V1,123456.000,A,2234.5678,N,11400.1234,E,0.00,0.0,100,0,0,0,0,0,0,0,0#";
    channel.writeInbound(Unpooled.copiedBuffer(altMsg, StandardCharsets.US_ASCII));
    
    Object result = channel.readInbound();
    assertNotNull("Alternative path should decode successfully", result);
    assertTrue(result instanceof Position);
    // ... verify position fields
}
```

✅ **Correct** (verify the default/primary path still works):
```java
@Test
public void testDecodePrimaryPath() throws Exception {
    YwtProtocolDecoder decoder = new YwtProtocolDecoder(new Protocol("ywt"));
    Channel channel = EmbeddedChannelFactory.build(decoder);
    
    String primaryMsg = "*XX,123456789012345,V1,123456.000,A,2234.5678,N,11400.1234,E,0.00,0.0,100#";
    channel.writeInbound(Unpooled.copiedBuffer(primaryMsg, StandardCharsets.US_ASCII));
    
    Object result = channel.readInbound();
    assertNotNull("Primary path should decode successfully", result);
    assertTrue(result instanceof Position);
}
```

❌ **Incorrect** (only tests one decoding path, missing the alternative branch):
```java
@Test
public void testDecode() throws Exception {
    YwtProtocolDecoder decoder = new YwtProtocolDecoder(new Protocol("ywt"));
    Channel channel = EmbeddedChannelFactory.build(decoder);
    String msg = "*XX,123456789012345,V1,123456.000,A,2234.5678,N,11400.1234,E,0.00,0.0,100#";
    channel.writeInbound(Unpooled.copiedBuffer(msg, StandardCharsets.US_ASCII));
    assertNotNull(channel.readInbound());
    // Only one message format tested — alternative decoding path completely uncovered
}
```