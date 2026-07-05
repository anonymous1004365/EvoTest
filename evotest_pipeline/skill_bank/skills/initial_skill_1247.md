---
name: khd-protocol-decoder-state-mutation
description: When writing tests for protocol decoders that maintain internal state
  (like KhdProtocolDecoder's timezone or buffer state), test that message decoding
  correctly handles stateful interactions where earlier messages mutate state that
  affects later decoding. The TG should verify that the decoder correctly processes
  messages in sequence when state is mutated during decoding.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
- STATE_MUTATION
- PROTOCOL_MESSAGE_DECODING
test_pattern: STATE_TEST
---

# khd-protocol-decoder-state-mutation

## Instructions

# Khd Protocol Decoder State Mutation Test Skill

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., `KhdProtocolDecoder`) that decodes device messages and has internal mutable state (such as timezone fields, buffer fields, or connection-specific state) that is modified during `decode()` calls
- THEN the TG should write a state-based test that:
  1. Creates the decoder instance
  2. Captures or inspects the internal state **before** calling decode
  3. Calls `decode()` with a test message that causes state mutation
  4. Captures or inspects the internal state **after** calling decode
  5. Verifies the state changed correctly (e.g., timezone is set from default/null to expected value, buffer is updated)
  6. Verifies the decoded result (e.g., the returned position object) contains the expected values

- Include concrete assertions about the state change:
  - Assert that fields like `timeZone`, `lastFrame`, or buffer fields are non-null after decode when they were null/empty before
  - Assert that the decoded position object contains expected values (e.g., position.getValid(), position.getLatitude(), position.getLongitude(), position.getDeviceTime())

- Common pitfalls to avoid:
  - Testing only the returned position object without verifying the decoder's internal state was correctly mutated
  - Not testing that state mutated by one decode call persists and affects subsequent decode calls
  - Using a single decode call when the bug manifests only across multiple sequential decode calls
  - Not checking both the decoded result AND the side effects on the decoder's internal fields

- Example of correct test code:
```java
@Test
public void testDecodeStateMutation() throws Exception {
    KhdProtocolDecoder decoder = new KhdProtocolDecoder(null);
    
    // Capture initial state
    String deviceId = ...;
    ByteBuf buf = Unpooled.copiedBuffer(hexStringToByteArray("...message hex..."));
    
    // Decode
    Object result = decoder.decode(null, new Channel() { ... }, deviceId, buf);
    
    // Verify decoded position
    assertNotNull(result);
    assertTrue(result instanceof Position);
    Position position = (Position) result;
    assertTrue(position.getValid());
    
    // Verify internal state was mutated (e.g., timezone was set)
    Field timeZoneField = KhdProtocolDecoder.class.getDeclaredField("timeZone");
    timeZoneField.setAccessible(true);
    assertNotNull(timeZoneField.get(decoder)); // state was set
}
```

- Example of incorrect test code (pitfall):
```java
@Test
public void testDecodeWrong() throws Exception {
    KhdProtocolDecoder decoder = new KhdProtocolDecoder(null);
    // Testing only one message in isolation, without checking internal state
    Object result = decoder.decode(null, null, "123", someBuffer);
    assertNotNull(result);
    // Missing: verification of internal state mutation
    // Missing: test with sequential messages that rely on mutated state
}
```