---
name: protocol-parser-state-override
description: When a protocol decoder has a mutable state field (like `protocol`) that
  gets modified during message processing, alternative decoding paths may override
  it without reset. The TG should test decoding flows that exercise multiple alternative
  code paths to verify state is not corrupted.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
- PROTOCOL_PARSER_STATE_OVERRIDE
test_pattern: STATE_TEST
---

# protocol-parser-state-override

## Instructions

# Protocol Parser State Override Detection

## Instructions

- WHEN the TG encounters a protocol decoder/parser class that contains a mutable state field (e.g., `String protocol`, `int mode`, `Object state`) that can be set or modified during the decoding of a message
- THEN the TG should write a test that:
  1. First decodes a message that triggers one path (e.g., path A) — one that sets the state field to a specific value
  2. Then decodes a second message that triggers an alternative path (e.g., path B) — one that relies on the state field having a correct/reset value
  3. Verify that the state field after the second decode is correct/expected (e.g., matches what would result from decoding the second message independently)
  4. Alternatively, test decoding the second message FIRST to confirm the state is correctly initialized, then decode the first message, then decode the second message again and verify the state is correct

- Common pitfalls:
  - Testing only a single message in isolation — this misses bugs caused by message ordering / state contamination
  - Assuming the decoder resets its state between messages — the bug is precisely that it DOESN'T reset
  - Testing only the happy path where messages are decoded in a "clean" order
  - Not checking the final state/result after the sequence of decodes

- Example correct test pattern (Java pseudocode):
  ```java
  @Test
  public void testAlternativePathsDontCorruptState() {
      ProtocolDecoder decoder = new ProtocolDecoder(someChannel);
      
      // First, trigger path that sets state
      decoder.decode(channel, remoteAddress, msg1);  // msg1 triggers path A, sets protocol = "XYZ"
      
      // Second, trigger alternative path that should use/reset state
      Object result = decoder.decode(channel, remoteAddress, msg2);  // msg2 triggers path B
      
      // Verify the result is correct despite previous state pollution
      assertNotNull(result);
      // Verify specific fields in result are as expected for msg2 alone
      assertEquals(expectedFieldValue, result.getSomeField());
  }
  ```

- Example incorrect test (single message only — misses the bug):
  ```java
  @Test
  public void testSinglePath() {
      ProtocolDecoder decoder = new ProtocolDecoder(someChannel);
      Object result = decoder.decode(channel, remoteAddress, someMessage);
      assertNotNull(result);
      // This never exposes the state override bug
  }
  ```