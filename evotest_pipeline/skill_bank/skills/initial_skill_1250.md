---
name: protocol-decoder-alternative-path-state
description: When a protocol decoder has alternative decoding paths (e.g., fallback
  to a different protocol), the test should verify that the decoder correctly resets
  or manages shared state when switching between paths. Missing state cleanup can
  cause incorrect decoding results in subsequent messages.
code_tags:
- VALIDATION
- NULL_CHECK
- ALTERNATIVE_PROTOCOL_DECODING
- STATE_MUTATION
test_pattern: STATE_TEST
---

# protocol-decoder-alternative-path-state

## Instructions

# Protocol Decoder Alternative Path State Management

## Instructions

- WHEN the TG encounters a protocol decoder class that implements `implements` from a base protocol decoder (like `BaseProtocolDecoder`) AND the class has **alternative decoding paths** (e.g., trying one protocol format first, then falling back to another different protocol format via `proceedObject` or similar delegation mechanism)
- THEN the TG should write a test that:
  1. First sends a message that triggers the **alternative/fallback decoding path** (the one that doesn't match the primary protocol format)
  2. Then immediately sends a valid message for the **primary protocol format**
  3. Verifies that the second message is decoded correctly (expecting a valid result, not `null` or an incorrect object)
  4. The test should produce a non-null result for the second message even though the first message triggered the fallback path
- The test should use the standard decoder test harness (e.g., extending a test base class with `testDecode` pattern) and send both messages as instances of the same decoded object type
- Common pitfalls to avoid:
  - Testing only the primary protocol path in isolation without setting up the alternative path first
  - Assuming that the alternative path does not affect internal state (e.g., cached attributes, decoder configuration)
  - Testing with only one message type rather than a sequence that exercises both paths
  - Using `assertNull` for the second message when the correct behavior is to produce a decoded position object

### Example (Correct)
```java
// Test that after an alternative/fallback decoding path is taken, 
// the primary protocol path still works correctly
@Test
public void testDecode() throws Exception {
    WialonProtocolDecoder decoder = new WialonProtocolDecoder(null);
    
    // First message: triggers the alternative/fallback decoding path
    // (e.g., a message from a different protocol like "AVL" that gets forwarded)
    Object result1 = decoder.decode(null, null, 
        new WialonFrameDecoderTest.Message("someMessage"));
    
    // Second message: a valid message for the primary protocol
    // This should be decoded successfully even after the fallback
    Object result2 = decoder.decode(null, null, 
        new WialonFrameDecoderTest.Message("someValidMessage"));
    
    assertNotNull("Second message should decode successfully after fallback path", result2);
    assertTrue("Result should be a position object", result2 instanceof Position);
}
```

### Example (Incorrect)
```java
// BAD: Only tests the primary protocol path in isolation
@Test
public void testDecode() throws Exception {
    WialonProtocolDecoder decoder = new WialonProtocolDecoder(null);
    
    // Only testing the happy path
    Object result = decoder.decode(null, null, 
        new WialonFrameDecoderTest.Message("someValidMessage"));
    
    assertNotNull(result);
    // Missing: test that the alternative path doesn't corrupt state
}
```