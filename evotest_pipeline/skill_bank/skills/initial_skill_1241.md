---
name: haicom-protocol-decode-null-position
description: Teaches the TG to test protocol decoders that may produce null/empty
  position objects, especially when the buggy version fails to check for valid position
  data before constructing response messages.
code_tags:
- NULL_CHECK
- VALIDATION
- BOUNDARY_CHECK
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: EXCEPTION_TEST
---

# haicom-protocol-decode-null-position

## Instructions

# Haicom Protocol Decoder Null Position Handling

## Instructions

**WHEN** the TG encounters a protocol decoder class (e.g., `HaicomProtocolDecoder`) that extends `BasePositionProtocolDecoder` and overrides a `decode` method (e.g., `decode` or `decodePosition`):

- **THEN** the TG should verify that the decoder properly handles cases where a helper method (such as `decodePosition`) returns `null`, especially when the `null` result is used to construct a downstream response (like a `Protocol` command response or acknowledgment).

- **Specifically**, when a protocol decoder's `decode` method calls `decodePosition` (or similar position-decoding logic), and that call returns `null`:
  - The buggy version may proceed to call methods on the `null` result (e.g., accessing `position.getProtocol()` without a null check), causing a `NullPointerException`.
  - The TG's test should send a valid protocol message (from real device data, e.g., a Haicom device heartbeat or other valid frame) that triggers the alternative decoding path where `decodePosition` returns `null`, and **expect that the decoder does NOT throw a `NullPointerException`**.
  
- **Common pitfalls to avoid**:
  - Testing only the happy path where position decoding succeeds and returns a valid object.
  - Testing only with completely malformed/invalid data that fails earlier in the parsing chain.
  - Forgetting to test with valid protocol frames that legitimately produce no position (e.g., heartbeat/keepalive messages).
  - Not including the specific field or format that triggers the null-returning code path.

- **Concrete example (correct)**:
  ```java
  // Send a valid Haicom message that should not produce a position (e.g., a simple heartbeat)
  // Verify no exception is thrown
  assertThat(decoder.decode(channel, remoteAddress, msg), notNullValue());
  // Or verify the response is an instance of ProtocolCommand or similar
  ```

- **Concrete example (incorrect)**:
  ```java
  // ❌ Only testing the standard position-decoding path
  // ❌ Using completely random bytes that fail early
  // ❌ Expecting a position object when the message type doesn't provide one
  ```