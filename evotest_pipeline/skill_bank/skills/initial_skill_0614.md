---
name: gl200-protocol-message-decoding-ambiguity
description: When a protocol decoder parses data from a received message and uses
  the same field values to determine message type, tests must ensure correct handling
  when a parameterized value could match multiple distinct message patterns. Use this
  skill to test ambiguity resolution in custom protocol decoders.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# gl200-protocol-message-decoding-ambiguity

## Instructions

# GL200 Protocol Message Decoding Ambiguity

## Instructions

- WHEN the TG encounters a custom protocol decoder (e.g., extending `BaseProtocolDecoder`) that parses raw protocol messages by reading string fields and matching against known patterns using `hasAttribute`, `matches`, or similar logic
- THEN the TG should write parametric tests that:
  1. Feed a message string where a field value (e.g., an IMEI or device ID) can be interpreted as belonging to more than one message type
  2. Verify the correct position (index) is used when checking field content after splitting/parsing the message string
  3. Assert the decoder produces the expected `DecoderResult` object (e.g., returns the decoded position or throws the expected exception for unknown messages)
  4. Use at least two different devices with the same IMEI prefix to test that the decoder can distinguish them correctly

- Common pitfalls to avoid:
  - Testing with only one device or one simple message pattern (which would not expose index/offset errors)
  - Assuming that field content at a fixed position is unique across all message types
  - Not including leading zeros or other variations in device IDs that could cause misinterpretation
  - Using an incomplete message that matches only one pattern (the bug may only appear when the same field could match two patterns)

### Correct Example (exposes the bug)

```java
@Test
public void testDecodeAmbiguous() throws Exception {
    Gl200ProtocolDecoder decoder = new Gl200ProtocolDecoder(new Gl200Protocol());
    // Device 1: IMEI "123456789012345" — first field after header
    // Device 2: IMEI "123456789012346" — first field after header
    // Both are parsed correctly when the decoder uses correct index (0) for IMEI
    verifyPosition(decoder, binary("+INIT,123456789012345,1"));
    verifyPosition(decoder, binary("+INIT,123456789012346,1"));
}
```

### Incorrect Example (misses the bug)

```java
@Test
public void testDecodeSimple() throws Exception {
    Gl200ProtocolDecoder decoder = new Gl200ProtocolDecoder(new Gl200Protocol());
    // Only testing one message type with one device — does not verify that
    // the decoder correctly associates IMEI field with the right index
    verifyPosition(decoder, binary("+INIT,123456789012345,1"));
}
```