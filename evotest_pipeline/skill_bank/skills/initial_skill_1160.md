---
name: blackkite-protocol-decoder-npe-on-alternative-path
description: ''
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# blackkite-protocol-decoder-npe-on-alternative-path

## Instructions

# BlackKite Protocol Decoder: NPE on Alternative Decoding Path

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g. `BlackKiteProtocolDecoder`) that implements `decode` with both a **primary/heuristic path** and an **alternative/heuristic path** (e.g., one path handling `String` commands like `"#L#..."`, another path for `"#D#..."` or other message types)
- THEN the TG should **write a test that sends a message type that triggers the alternative/heuristic decoding branch**, specifically:
  - A message that does NOT match the primary command type (which expects `getDeviceId()` fields or similar identification)
  - For example, with `BlackKiteProtocolDecoder`, the primary path decodes `#L#...` messages (which contain sent date and identification) — the alternative path decodes other messages like `#D#...`
  - Test with raw byte/string input that triggers the **else/alternative branch** of the decoder's main if-else or switch logic
  - Verify that **no NullPointerException** is thrown; the test should decode successfully and return a non-null result (or handle the error gracefully)
- WHEN writing such a test, the TG MUST ensure the test:
  1. Creates a `Channel` and a `SocketAddress` (can use `new InetSocketAddress(0)`)
  2. Calls the decoder's `decode(channel, address, message)` method directly with the alternative message
  3. Asserts the decoded result is not null (or contains the expected position/object type)
- Common pitfalls:
  - ❌ Testing only the primary message type (`#L#...`), missing the alternative path (`#D#...`)
  - ❌ Not verifying that the result is non-null on the buggy version (the NPE would fail the decode call itself)
  - ❌ Using `null` for channel or address arguments instead of proper mocks/instances

### Correct example (tests the alternative decoding path):
```java
@Test
public void testDecodeAlternativePath() throws Exception {
    var decoder = new BlackKiteProtocolDecoder();
    var channel = mock(Channel.class);
    var address = new InetSocketAddress(0);
    // This message triggers the alternative (non-#L#) decoding path
    String msg = "#D#061616141800260,,,100,0,0,0,0,0,0,0,0,0,0,0#";
    var result = decoder.decode(channel, address, msg);
    // On the fixed version, this should succeed
    assertNotNull(result);
}
```

### Incorrect example (tests only the primary path):
```java
@Test
public void testDecodePrimaryOnly() throws Exception {
    var decoder = new BlackKiteProtocolDecoder();
    var channel = mock(Channel.class);
    var address = new InetSocketAddress(0);
    // Only tests the #L# path — misses the alternative path bug
    String msg = "#L#200429000860,,,100,0,0,0,0,0,0,0,0,0,0,0#";
    var result = decoder.decode(channel, address, msg);
    assertNotNull(result);
}
```