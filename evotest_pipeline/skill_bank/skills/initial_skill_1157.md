---
name: decoder-protocol-null-handling
description: When writing tests for protocol decoders that convert bytes to typed
  fields, the TG should test that null or absent fields are handled gracefully and
  do not cause NullPointerException or silent failures. This skill applies to any
  scenario where a decoder parses variable-length or optional protocol fields.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# decoder-protocol-null-handling

## Instructions

# Decoder Protocol Null Handling

## Instructions

- WHEN the TG encounters a protocol decoder that parses positional or length-prefixed binary fields (e.g., status bits, IMEI, ignition, device type, etc.) and converts them into typed object fields (Boolean, String, Integer, CtTypeReference, etc.)
- THEN the TG should write tests that:
  1. Provide input where specific optional fields are absent (zero length, missing bytes, or null marker values)
  2. Verify that the decoder does NOT throw `NullPointerException` or any unchecked exception on the buggy version
  3. Verify that the resulting decoded object contains expected default values (e.g., `null`, `false`, empty string) for the absent fields
- Include at least one test case where an entire optional data section is omitted (empty payload) from a correct-length frame
- Common pitfalls:
  - Testing only with fully populated, well-formed payloads (happy path) — this misses null-handling bugs
  - Assuming a field like "ignition" or "status" will always be present and non-null
  - Using a mock or stub that supplies all fields, bypassing the real null-reception path

### Correct Example

```java
// BceProtocolDecoder: send a frame with zero bytes for the optional parameters section
@Test
public void testDecodeWithNullOptionalFields() {
    BceProtocolDecoder decoder = new BceProtocolDecoder(null);
    // Arrange: minimal valid header + zero-length payload for optional fields
    ByteBuf buf = Unpooled.buffer();
    buf.writeShort(0xABCD);  // header
    buf.writeByte(0x00);     // length indicating zero optional fields follow
    // Act + Assert: should not throw NPE
    assertDoesNotThrow(() -> decoder.decode(null, null, buf));
}
```

### Incorrect Example

```java
// BAD: Only tests a fully populated payload
@Test
public void testDecode() {
    BceProtocolDecoder decoder = new BceProtocolDecoder(null);
    ByteBuf buf = Unpooled.buffer();
    // All fields present — never tests the null path
    buf.writeShort(0xABCD);
    buf.writeByte(0x0F);  // all fields present flag
    buf.writeBytes(...);  // all optional data present
    Object result = decoder.decode(null, null, buf);
    assertNotNull(result);
}
```