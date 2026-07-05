---
name: protocol-decoder-null-message-read
description: When a protocol decoder reads data from a position/device message that
  may be null, tests must verify that null-safe access is used to avoid NullPointerException
  during decoding.
code_tags:
- ARGUMENT_VALIDATION
- ALTERNATIVE_PROTOCOL_DECODING
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# protocol-decoder-null-message-read

## Instructions

# Protocol Decoder Null Message Read

## Instructions

- WHEN the TG encounters a protocol decoder (e.g., `L100ProtocolDecoder`) that reads data such as network identifiers, phone numbers, or other fields from a position or device message object
- AND the decoder accesses methods of that object (e.g., `getNetwork().getCellTowers()`, `getDeviceMSISDN()`, `getOutdated()`, etc.)
- THEN the TG MUST write a test that sends a message that triggers the alternative decoding code path where the message object or its nested fields are `null`
- The test MUST expect a clean decode (no NullPointerException) on the fixed version, meaning the null should be handled gracefully (e.g., skipped or defaulted)
- On the buggy version, the test MUST trigger a NullPointerException (or similar uncaught exception) when the decoder attempts to dereference a null value without a null check

### Common Pitfalls

- Testing only the primary/standard decoding path where all fields are populated — the bug is on an alternative path (e.g., partial message, missing fields)
- Testing with a null device session object but forgetting that the bug is about a null field *within* a non-null message (e.g., `cellTowers` being null when the protocol includes only a partial network)
- Mistaking the source of null: it is not the device session that is null, but the result of a method call on the decoded message (e.g., `getNetwork()` returns null, and then `.getCellTowers()` is called on it)

### Example

Correct approach (what the test should do):
```java
// Create a buffer with a message that triggers the alternative decode path
// where getNetwork() returns null but the decoder still calls getCellTowers() on it
ByteBuf buf = Unpooled.copiedBuffer("...partial message...", StandardCharsets.US_ASCII);
try {
    decoder.decode(null, null, buf);
    fail("Expected NullPointerException on buggy version");
} catch (NullPointerException e) {
    // expected on buggy version
}
```

Incorrect approach (what misses the bug):
```java
// Only tests the happy path where all network fields are present
ByteBuf buf = Unpooled.copiedBuffer("...full message with network data...", StandardCharsets.US_ASCII);
Position position = decoder.decode(null, null, buf);
assertNotNull(position);
// This passes on both versions and does not catch the bug
```