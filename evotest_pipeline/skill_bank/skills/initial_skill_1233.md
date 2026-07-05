---
name: granit-protocol-decode-message-type
description: When decoding protocol messages with message type fields, verify that
  the decoder handles unexpected or null message types without throwing NullPointerException.
  Tests should cover edge cases where protocol message type codes are invalid or missing.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# granit-protocol-decode-message-type

## Instructions

# Granit Protocol Decoder Message Type Validation

## Instructions

WHEN the TG encounters a protocol decoder that reads a message type field (e.g., an integer type code) from a binary buffer and uses it to determine parsing logic or construct a response object,

- THEN the TG should write a test that sends a message with an **invalid, unrecognized, or missing message type code** to the decoder.
- The test must verify that the decoder **does not throw a NullPointerException** and instead either returns `null`, throws a meaningful exception (e.g., `IllegalArgumentException`), or gracefully handles the invalid type.
- If the protocol decoder uses an enum or a map to dispatch based on message type, test with **all possible invalid values** including `0`, negative values, and values outside the expected range.
- The test should use the decoder's existing test infrastructure (e.g., `BasePipelineTest`, `ProtocolTest`) and send a binary frame constructed with the correct frame format but with an invalid type field.

Common pitfalls to avoid:
- Testing only with valid/recognized message types (happy path), which misses null pointer bugs in the error handling path.
- Assuming the decoder will gracefully handle unknown types without testing it explicitly.
- Forgetting to test boundary values (e.g., type code `0`, type code `-1`, type code just above the maximum known type).
- Testing the decoder in isolation without verifying the actual decoded method returns or exception behavior (i.e., just checking the pipeline processes without asserting on the result).

### Correct Example (conceptual)
```java
@Test
public void testDecodeWithInvalidMessageType() {
    GranitProtocolDecoder decoder = new GranitProtocolDecoder(null);
    // Construct a buffer with an invalid type code (e.g., 0xFF)
    ByteBuf buf = Unpooled.buffer();
    buf.writeByte(0xFF); // invalid type
    // ... write other required fields ...
    assertThrows(Exception.class, () -> {
        decoder.decode(null, null, buf);
    });
}
```

### Incorrect Example (conceptual)
```java
@Test
public void testDecodeWithInvalidMessageType() {
    GranitProtocolDecoder decoder = new GranitProtocolDecoder(null);
    ByteBuf buf = Unpooled.buffer();
    buf.writeByte(0xFF);
    // ... write other required fields ...
    Object result = decoder.decode(null, null, buf);
    // This test passes even if NPE is thrown because we don't assert
}
```