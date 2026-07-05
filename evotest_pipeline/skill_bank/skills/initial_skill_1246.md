---
name: protocol-command-type-routing-for-non-position-messages
description: When a protocol decoder matches a general pattern but different command
  types (e.g., "CC", "MQ", "TX") carry non-position data, the decoder must return
  null (not a malformed Position). Tests should verify that command-only messages
  return null rather than attempting position decoding.
code_tags:
- NULL_CHECK
- VALIDATION
- ACCESS_CONTROL_EVALUATION
- PROTOCOL_COMMAND_ROUTING
test_pattern: STATE_TEST
---

# protocol-command-type-routing-for-non-position-messages

## Instructions

# Protocol Command-Type Routing for Non-Position Messages

## Instructions

WHEN the TG encounters a protocol decoder that parses messages matching a general regex pattern with a command/type field (e.g., `([^,]{2})` capturing values like "HB", "CC", "MQ", "TX") and the decoder does NOT have explicit conditional routing based on the command value, THEN the TG should test that non-position command types return null instead of a malformed Position.

For example, in `EasyTrackProtocolDecoder`, the pattern matches all `*ET,...` messages regardless of command type ("HB", "CC", "MQ", "TX", "GZ", "DW"), but only commands like "HB" and "DW" contain valid position data. Commands like "CC" (command response), "MQ" (message queue), "TX" (text message), and "GZ" (heartbeat/general) have different field layouts and should produce `null`.

The test should:
1. Create the decoder instance and call `verifyNull(decoder, text(...))` with command types that are NOT position-bearing (e.g., "CC", "MQ", "TX", "GZ")
2. Verify that the decoder does NOT throw an exception but returns null for these messages
3. For position-bearing commands ("HB", "DW"), verify they produce valid `Position` objects using `verifyPosition(...)`

**Common pitfalls:**
- Only testing position-bearing messages and assuming all matched inputs produce positions
- Assuming non-position commands throw exceptions — they should gracefully return null
- Not including command types with different field formats (e.g., "CC" has `0.0,V` instead of `A,<hex date>`)
- Testing with only one non-position command type instead of multiple variations

**Correct example:**
```java
verifyNull(decoder, text("*ET,358155100048430,CC,0.0,V,100603,141817,..."));
verifyNull(decoder, text("*ET,358155100054249,MQ"));
verifyNull(decoder, text("*ET,358155100054249,TX,A,100b06,053230"));
verifyNull(decoder, text("*ET,135790246811221,GZ,0001,0005"));
verifyPosition(decoder, text("*ET,358155100054249,HB,A,100b06,053318,..."));
```

**Incorrect example (only testing position messages):**
```java
verifyPosition(decoder, text("*ET,358155100054249,HB,A,100b06,053318,..."));
verifyPosition(decoder, text("*ET,135790246811221,DW,A,0A090D,101C0D,..."));
// Missing: non-position command types that should return null
```