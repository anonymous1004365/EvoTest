---
name: alternative-protocol-decoding-path
description: WHEN the TG encounters protocol decoders that have alternative decoding
  paths (e.g., different message types, fallback parsing logic), THEN it should test
  that all paths correctly populate the decoder's state fields to prevent NPEs or
  partial state from one path leaking into another.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding Path

## Instructions

WHEN the TG encounters a protocol decoder class (e.g., `VtfmsProtocolDecoder`) that implements a `decode()` method with **alternative decoding paths**—such as different `if/else` branches for handling various message types, or one primary path and one fallback/error path—THEN the TG should write a test that:

1. **Sends each distinct message type** through the decoder to verify each alternative path independently.
2. **Verifies that ALL state fields** (e.g., the decoder's own mutable fields like `position`, `deviceId`, etc.) are properly set or updated **after each path executes**, not just after one path.
3. **Checks that no critical state left over from one path causes a NullPointerException in another path** — especially when the decoder reuses a single position object across multiple messages.
4. **Expects that a NullPointerException or similar runtime exception** should NOT occur when processing valid messages of different types in sequence.

**Common pitfalls:**
- Testing only a single message type (e.g., only the "main" protocol message) while ignoring the alternative/fallback path.
- Assuming that because a decoder successfully parsed one message type, all internal state is correct for all message types.
- Not verifying that the decoder's mutable fields are initialized (non-null) before being used across paths.
- Using mocks that don't exercise the actual branching logic in the decode method.

**Example (correct):**
```java
@Test
public void testDecodeMultipleMessageTypes() throws Exception {
    VtfmsProtocolDecoder decoder = new VtfmsProtocolDecoder(new TestProtocol());
    
    // First message type (primary path)
    String msg1 = "*123456789012345,HB,20241201000000,1,2,3#";
    decoder.decode(null, null, msg1);
    
    // Second message type (alternative path)
    String msg2 = "*123456789012345,KD,20241201000000,1,2,3#";
    assertDoesNotThrow(() -> decoder.decode(null, null, msg2));
}
```

**Example (incorrect — missing alternative path):**
```java
@Test
public void testDecodeOnlyOneType() throws Exception {
    VtfmsProtocolDecoder decoder = new VtfmsProtocolDecoder(new TestProtocol());
    // Only tests the primary path, never exercises the alternative path
    String msg = "*123456789012345,HB,20241201000000,1,2,3#";
    decoder.decode(null, null, msg);
    // Partial state may leave decoder in invalid state for other messages
}
```