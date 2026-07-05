---
name: navigil-protocol-null-decode
description: ''
code_tags:
- EXCEPTION_TRANSLATION
- NULL_CHECK
- VALIDATION
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: EXCEPTION_TEST
---

# navigil-protocol-null-decode

## Instructions

# Navigil Protocol Null Alternative Decode Path

## Instructions

- WHEN the TG encounters a protocol decoder that dispatches to different decode paths based on a message type identifier (e.g., a `switch` statement on an integer or string message type), AND one of those paths is a **catch-all or default branch** that tries to parse the message with a fallback approach (e.g., calling a generic `decode` method on a different type or parsing raw data),
- THEN the TG should write a test that sends a **message with an unrecognized/unknown message type** that triggers the default/alternative decoding path, and verify that:
  1. The decoder does **not** throw a `NullPointerException` when the alternative path processes the message.
  2. The decoder returns a valid result (a list of positions, a `WktResponse`, or whatever the return type is) or gracefully handles the unknown type — at minimum, it must not crash.
  3. The test should exercise the specific code path where the alternative decoder returns `null` or fails to parse, and where the parent decoder then tries to use that `null` result without a null check.

- **Common pitfalls (what the TG might do wrong without this skill):**
  - Testing only known/valid message types, which never reach the alternative decoding path.
  - Assuming the default branch is safe because it simply delegates to another decoder — ignoring that the delegate may return `null`.
  - Not sending messages with raw or malformed payload data that forces the alternative path to fail.

### Example (Correct — catching the NPE)
```java
// Correct: tests the unknown message type that triggers the default path
@Test
public void testDecodeWithUnknownType() throws Exception {
    NavigilProtocolDecoder decoder = new NavigilProtocolDecoder(null);
    // Channel buffer with an unknown message type that forces fallback parsing
    ByteBuf buf = Unpooled.copiedBuffer(new byte[]{0x01, 0x02, 0x03, 0x04});
    // Should NOT throw NullPointerException
    Object result = decoder.decode(null, null, buf);
    assertNotNull(result);
}
```

### Example (Incorrect — missing the null decode path)
```java
// Incorrect: only tests valid message types, never exercises the default branch
@Test
public void testDecodeValidMessage() throws Exception {
    NavigilProtocolDecoder decoder = new NavigilProtocolDecoder(null);
    ByteBuf buf = Unpooled.copiedBuffer(validMessageBytes);
    Object result = decoder.decode(null, null, buf);
    assertNotNull(result);
}
// This test passes on both buggy and fixed, so it does NOT catch the bug!
```