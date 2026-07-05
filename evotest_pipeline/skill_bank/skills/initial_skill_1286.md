---
name: protocol-alternative-decoding-path-state
description: When a protocol decoder has an alternative decoding path (e.g., fallback
  or secondary parser) that modifies shared decoder state (like position/offset) before
  reading data, the test should exercise that path with different message types to
  ensure the decoder state is correctly managed. Use this skill when testing protocol
  decoders with multiple message format pathways.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- ARGUMENT_VALIDATION
- VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# protocol-alternative-decoding-path-state

## Instructions

# Protocol Alternative Decoding Path State Management

## Instructions

- **WHEN** the TG encounters a protocol decoder class (e.g., `StarLinkProtocolDecoder`) that has an alternative decoding path — such as a fallback or secondary message parser that modifies a shared decoder state field (e.g., `position`, `offset`, or `bufferIndex`) before reading or decoding data:
  - **THEN** the TG should write a test that exercises **both** the primary and alternative decoding paths in sequence, sending different message types to verify the decoder state is **correctly reset or managed** after the alternative path executes.
  - **THEN** the test should verify that after the alternative path runs, the primary path still produces correct results — not throwing unexpected exceptions (e.g., `ArrayIndexOutOfBoundsException`, `IndexOutOfBoundsException`, or producing wrong decoded field values).
  - **THEN** include concrete test inputs that trigger the alternative path (e.g., a message with a different format, size, or identifier) followed by a normal message that uses the primary path — assert that both decode correctly.
  - **Common pitfall**: Testing only the primary decoding path in isolation, or testing only the alternative path without checking that the decoder state (e.g., position/offset fields) is properly restored for subsequent decoding.
  - **Common pitfall**: Not verifying that the decoder can handle messages in **any order** — the alternative path might leave internal counters/pointers in an inconsistent state that causes the next decode to fail.

### Example (Correct)

```java
// Protocol decoder test that exercises both decoding paths
@Test
public void testDecodeWithAlternativePathStateReset() throws Exception {
    StarLinkProtocolDecoder decoder = new StarLinkProtocolDecoder(...);
    
    // Step 1: Send a message that triggers the alternative decoding path
    // (e.g., a configuration/setup message with different header format)
    Object altResult = decoder.decode(null, null, createAlternativeMessage());
    assertNotNull("Alternative path should produce result", altResult);
    
    // Step 2: Send a normal data message that uses the primary decoding path
    // The decoder state MUST be clean/consistent after step 1
    Object primaryResult = decoder.decode(null, null, createNormalMessage());
    assertNotNull("Primary path should still work after alternative path", primaryResult);
    
    // Step 3: Verify the decoded fields are correct
    Position position = (Position) primaryResult;
    assertEquals(37.7749, position.getLatitude(), 0.0001);
    assertEquals(-122.4194, position.getLongitude(), 0.0001);
}
```

### Example (Incorrect — Missing State Reset Verification)

```java
// BAD: Only tests the alternative path in isolation
@Test
public void testDecodeAlternativePath() throws Exception {
    StarLinkProtocolDecoder decoder = new StarLinkProtocolDecoder(...);
    
    // Only tests one message type — doesn't verify state doesn't leak
    Object result = decoder.decode(null, null, createAlternativeMessage());
    assertNotNull(result);
    // The bug would remain hidden because no subsequent decode uses the primary path
}
```