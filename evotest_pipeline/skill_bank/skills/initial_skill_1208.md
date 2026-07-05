---
name: alternative-protocol-decoding-with-state-corruption
description: When a protocol decoder has alternative decoding paths that mutate shared
  state, test that each path produces correct results independently and that state
  is not corrupted across multiple decode calls.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-with-state-corruption

## Instructions

# Alternative Protocol Decoding with State Corruption

## Instructions

WHEN the TG encounters a protocol decoder class (e.g., extending `BaseProtocolDecoder`) that contains multiple alternative decoding paths (e.g., if/else chains, switch cases, or try/catch blocks that attempt different decoding approaches on the same channel buffer), THEN the TG should write a parametric test that:

1. **Test each alternative decoding path independently**: Provide multiple test messages, each designed to exercise a different alternative path in the decoder's `decode()`, `decodeBuffer()`, or similar method. Verify that each path returns the expected result (e.g., non-null decoded object, correct position data, correct frame decoding).

2. **Test state isolation across calls**: After decoding multiple messages through different alternative paths in sequence (without resetting the decoder), verify that state variables (e.g., `lastMillis`, `lastPosition`, protocol-specific internal counters/flags) do not corrupt subsequent decoding results.

3. **Test with incomplete/corrupted messages**: Include test cases with messages that are expected to fail one alternative path but succeed in another, verifying the decoder correctly falls through to the next alternative without throwing unexpected exceptions.

4. **Test with edge-case protocol buffers**: Include test messages with boundary values (e.g., empty buffer, single byte buffers, buffers with maximum allowed size) to ensure no alternative path throws an `IndexOutOfBoundsException` or similar.

### Common Pitfalls

- Testing only the "happy path" — the most common message format — while missing the alternative decoding logic entirely.
- Testing alternative paths in isolation but not verifying that state mutations from one path affect another.
- Assuming the decoder resets internal state between `decode()` calls; the same decoder instance may be reused.
- Not testing with realistic malformed data that exercises fallback paths.
- Testing only primitive-type parameters while ignoring `CtTypeReference` / generic type parameters that trigger different decoding branches.

### Correct Example (Java with JUnit 5)

```java
@Test
void testAlternativeDecodingPaths() {
    RitiProtocolDecoder decoder = new RitiProtocolDecoder(null);
    
    // Path 1: Decode a standard position message
    ByteBuf buf1 = Unpooled.copiedBuffer(hexToBytes("...")); // standard message
    Object result1 = decoder.decode(null, null, buf1);
    assertNotNull(result1, "Standard message should decode to non-null position");
    assertTrue(result1 instanceof Position);
    
    // Path 2: Decode a heartbeat/status message (different type)
    ByteBuf buf2 = Unpooled.copiedBuffer(hexToBytes("...")); // heartbeat message
    Object result2 = decoder.decode(null, null, buf2);
    assertNotNull(result2, "Heartbeat should decode to non-null position");
    
    // State isolation: decoding should not corrupt decoder state
    ByteBuf buf3 = Unpooled.copiedBuffer(hexToBytes("...")); // standard message again
    Object result3 = decoder.decode(null, null, buf3);
    assertNotNull(result3, "State should not be corrupted by previous call");
    assertInstanceOf(Position.class, result3);
    
    // Path 3: Malformed message falling through to alternative path
    ByteBuf badBuf = Unpooled.copiedBuffer(hexToBytes("0xFF")); // malformed
    Object result4 = decoder.decode(null, null, badBuf);
    // Should still return a result via fallback, not throw
    assertNotNull(result4);
}
```

### Incorrect Example

```java
// BAD: Only tests one decoding path, no state isolation check
@Test
void testDecodeOnlyStandardMessage() {
    RitiProtocolDecoder decoder = new RitiProtocolDecoder(null);
    ByteBuf buf = Unpooled.copiedBuffer(hexToBytes("...")); // only one message type
    Object result = decoder.decode(null, null, buf);
    assertNotNull(result);
    // Missing: other message types, state corruption, malformed input
}
```