---
name: protocol-decoder-template-parameter-type-validation
description: When writing tests for protocol decoders with template/parameterized
  type configurations, verify that the decoder correctly handles both the expected
  concrete types (e.g., String) and the raw parameterized types (e.g., a CtTypeReference
  or Type object) in its template resolution logic. Use STATE_TEST patterns to validate
  that internal decoder state (like channel templates) is correctly set and not silently
  corrupted when processing device-specific messages that provide type-resolved parameters.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# protocol-decoder-template-parameter-type-validation

## Instructions

# Protocol Decoder Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a protocol decoder class that uses a **template-based or type-resolved parameter mechanism** (e.g., building a channel identification string from a template that accepts both plain `String` values and `CtTypeReference` or other type objects passed as arguments), THEN it should write a test that sends a real device message or data buffer through the decoder's decode path and verify that the resulting decoded position/object has the **correct internal state** (e.g., the channel attribute is set to the expected value, not null, and not a wrong value like a stringified type name or an empty string).

- WHEN testing a decoder that resolves type parameters from a generic template (e.g., a template string `"{x},{y},{z}"` where arguments can be `String` or `Type` objects), THEN verify that when the argument is a **non-String type** (e.g., a `CtTypeReference` or Java `Type`), the decoder does **not** silently use `toString()` on that object (producing something like `"void C.T"`) but instead correctly handles it — either by extracting the actual type name or by properly formatting the value.

- WHEN the decoder uses a **loop over parameters where some are strings and some are type references**, THEN the test should simulate this by sending messages that exercise the mixed-parameter path. Include a concrete assertion that checks the final state of the decoded object (e.g., `assertEquals("expectedChannel", decoded.getChannel())`) and expect that the buggy version produces either a `null` value, an empty string, or an incorrectly formatted string in that field.

- **Common pitfall**: Testing only with simple `String` type parameters and never sending a message that exercises the **type-reference branch** of the template resolution. If the decoder has multiple code paths for parameter resolution (e.g., `if (arg instanceof CtTypeReference)`), the test must exercise ALL branches. Without this, the bug where type arguments produce garbage in the output will be missed.

- **Common pitfall**: Verifying only that no exception is thrown, without asserting on the **content** of the decoded position fields. The test must check specific field values (channel, device id, etc.) to catch silent data corruption.

### Correct Example (catches the bug)

```java
@Test
public void testDecodeWithTypeParameters() throws Exception {
    PretraceProtocolDecoder decoder = new PretraceProtocolDecoder(new Protocol("pretrace"));
    // ByteBuf containing a message that triggers template resolution where 
    // one argument is a CtTypeReference/Type object instead of a String.
    // This exercises the alternative code path that the bug introduced.
    ByteBuf buf = Unpooled.copiedBuffer(HexUtil.decodeHex("0d0a..."));
    // Verify the decoded position has the correct channel/attribute
    Position position = decoder.decode(null, null, buf);
    assertNotNull("Channel should not be null", position.getString(Position.KEY_CHANNEL));
    // The buggy version would set channel to something like "void C.T" or "" or null
    assertEquals("1", position.getString(Position.KEY_CHANNEL));
}
```

### Incorrect Example (misses the bug)

```java
@Test
public void testDecodeBasic() throws Exception {
    PretraceProtocolDecoder decoder = new PretraceProtocolDecoder(new Protocol("pretrace"));
    ByteBuf buf = Unpooled.copiedBuffer(HexUtil.decodeHex("0d0a..."));
    Position position = decoder.decode(null, null, buf);
    // Only checks no exception, never checks field content
    assertNotNull(position);
    // Misses the bug because it doesn't verify the corrupted channel value
}
```