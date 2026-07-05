---
name: format-format-detection-with-mutable-state
description: When a decoder uses a Boolean mutable field to remember which format
  was detected and retries with a different pattern on failure, test that the decoder
  correctly handles messages matching BOTH formats by sending them in sequence to
  verify state transitions don't cause the second format to fail silently.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# format-format-detection-with-mutable-state

## Instructions

# Format Detection with Mutable State

## Instructions

- WHEN the TG encounters a protocol decoder that uses a `Boolean` mutable field (e.g., `private Boolean newFormat`) to cache which message format was detected, and the decoder tries one pattern first, and on failure tries an alternative pattern on the **first message only**, then sets the state field for all subsequent messages:
  - THEN the TG MUST write a test that sends a message matching the **second** format first, followed by a message matching the **first** format, and verify both decode successfully.
  - THEN the TG MUST write a test that sends a message matching the **first** format first, followed by a message matching the **second** format, and verify both decode successfully.
- WHEN testing format auto-detection with state mutation (a `Boolean` field set from `null` to `true` or `false` after the first parse attempt):
  - THEN the TG MUST verify that the decoder does NOT permanently lock into the wrong format after an initial message that only matches one pattern. The test should send a sequence like: [new-format message, old-format message] and verify both return non-null `Position` objects.
  - THEN the TG MUST avoid the common pitfall of only testing messages of a single format in isolation, which would not expose the state mutation bug.

- WHEN verifying behavior across state transitions in `XirgoProtocolDecoder`:
  - THEN the TG should use `verifyPosition(decoder, text("..."))` which internally asserts a non-null Position is returned. The TG should NOT assume `verifyPosition` checks for specific field values — it only checks successful decode.
  - THEN the TG should be aware that sending an old-format message while `newFormat` field is `true` will cause a decode failure (return null) if the old-format message does not match `PATTERN_NEW`, and vice versa. The test must detect this by checking that `decoder.decode(...)` returns non-null for both formats in either order.

### Common Pitfalls

- **Testing only one format**: If the test only sends new-format or only old-format messages, it will not catch bugs where the format detection state machine deadlocks after mixing formats.
- **Assuming sequential independence**: The test might assume each `decoder.decode()` call is stateless. The `newFormat` field is a class-level `Boolean` that persists across calls, so the TG must test message ordering explicitly.
- **Relying on default state**: The initial state (`newFormat == null`) triggers auto-detection on the first message only. If the first message fails both patterns, the decoder returns null, but if it matches exactly one pattern, the state is locked. The test should cover the scenario where messages of opposite formats arrive.

### Correct Example

```java
// Test that old format followed by new format both work
XirgoProtocolDecoder decoder = new XirgoProtocolDecoder(new XirgoProtocol());

// First message: old format (triggers newFormat = false)
verifyPosition(decoder, text(
    "$$354660046140722,6001,2013/01/22,15:36:18,25.80907,-80.32531,7.1,19,165.2,11,0.8,11.1,17,1,1,3.9,2##"));

// Second message: new format (should decode even though newFormat is false)
verifyPosition(decoder, text(
    "$$352054058132185,4001,2017/04/21,00:01:05,32.54659,-116.90670,143.2,0,0,0,598,0.0,12,0.9,765840,7.0,14.5,19,1,1,0011,8.5,63.2,5,21999,184,255,671,207,100,185##"));
```

### Incorrect Example

```java
// BAD: only tests new format messages in isolation
XirgoProtocolDecoder decoder = new XirgoProtocolDecoder(new XirgoProtocol());
verifyPosition(decoder, text("$$352054058132185,4001,...185##"));
// This does NOT test what happens when an old-format message arrives after
// the state has been set to true. The bug would go undetected.
```