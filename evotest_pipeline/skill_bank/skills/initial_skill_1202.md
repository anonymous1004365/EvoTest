---
name: arknavx8-alternative-decoder-path-null-check
description: When a protocol decoder has alternative parsing paths (e.g., different
  message types), ensure that each path is tested independently for null pointer exceptions
  and that edge cases like empty or malformed parameter lists are covered.
code_tags:
- NULL_CHECK
- VALIDATION
- ARGUMENT_VALIDATION
test_pattern: PARAMETRIC_TEST
---

# arknavx8-alternative-decoder-path-null-check

## Instructions

# ArknavX8 Protocol Decoder: Alternative Decoding Path with Null-Unsafe Parameter Access

## Instructions

**WHEN** the TG encounters a protocol decoder class that handles multiple message types (e.g., via a switch statement on `type` or `msgType`) and uses alternative decoding paths where parameters like device identifiers, protocol values, or coordinates are parsed from a `ChannelBuffer` or argument list:

- **THEN** the TG should write **parametric tests** that feed each alternative decoding branch with malformed, truncated, or empty payloads (e.g., `ChannelBuffer` with fewer readable bytes than the decoder expects for that branch).
- **THEN** the TG should verify that the decoder does **not** throw a `NullPointerException` when an optional parameter or sub-message is missing from that branch.
- **THEN** the TG should test each `case`/`if` branch in isolation by constructing a minimal `ChannelBuffer` that triggers only that path but is missing one required parameter.
- **Mistake to avoid**: Do NOT test only the "happy path" where all parameters are present. Do NOT assume that because one message type works, all message types are safe. Do NOT test only with the full message — test each branch individually with incomplete data.

### Example (Correct)

```java
// Test the alternative decode path (e.g., type 1) with missing device identifier
@Test
public void testDecodeWithMissingDeviceId() throws Exception {
    ArknavX8ProtocolDecoder decoder = new ArknavX8ProtocolDecoder();
    // Build a ChannelBuffer that triggers the alternative path but lacks the device ID
    // Expected: should return null or throw a meaningful exception, NOT NullPointerException
    assertThrows(NullPointerException.class, () -> {
        decoder.decode(null, null, buffer);
    });
}
```

### Example (Incorrect)

```java
// Incorrect: Only tests the main path with full data — misses the bug in the alternative path
@Test
public void testDecode() throws Exception {
    ArknavX8ProtocolDecoder decoder = new ArknavX8ProtocolDecoder();
    // Only tests with a well-formed message of the default type
    Object result = decoder.decode(null, null, getFullTestBuffer());
    assertNotNull(result);
}
```

### What to look for
- A `switch` or `if-else` chain on `type`/`msgType` values inside the `decode` method.
- Instructions that read fixed positions from a buffer (e.g., `buffer.readUnsignedByte()`, `buffer.readInt()`) without checking `buffer.readableBytes()`.
- A branch that reads a parameter and then uses it to look up something (e.g., `getDeviceSession()`, `getChannel()`) — this is the prime NPE candidate if the parameter is null/empty.
- Message type bytes or identifiers that are parsed before the switch, meaning the branch-specific parsing happens only for certain types.