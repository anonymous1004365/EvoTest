---
name: protocol-decoder-exception-robustness
description: When writing tests for protocol decoders that parse binary/byte data
  from devices, the TG should test that decoders handle malformed or incomplete messages
  gracefully without throwing NullPointerException or other uncaught runtime exceptions.
code_tags:
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# protocol-decoder-exception-robustness

## Instructions

# Protocol Decoder Exception Robustness

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., any class that implements `extends BaseProtocolDecoder` or similar) that parses incoming byte buffers from device messages
- THEN the TG should write a test that passes a malformed or incomplete message (e.g., a `ChannelBuffer` with insufficient length, unexpected content, or null fields) and verify that the decoder does NOT throw an uncaught `NullPointerException`, `IndexOutOfBoundsException`, or similar runtime exception
  - The test should expect a graceful failure mode: returning `null` from the decode method, or throwing a checked exception, but NOT an unhandled RuntimeException
  - Use concrete assertions like `assertNull(result)` or `assertThrows(CheckedException.class, () -> decoder.decode(...))`
- Common pitfalls:
  - Testing only with well-formed, valid messages that only exercise the happy path
  - Assuming that null checks or guards exist in the decoder when they may be missing
  - Not testing empty or truncated ChannelBuffer inputs
- Correct example:
  ```java
  @Test
  public void testDecodeWithIncompleteMessage() {
      Gl100ProtocolDecoder decoder = new Gl100ProtocolDecoder();
      ChannelBuffer buf = ChannelBuffers.wrappedBuffer(new byte[]{0x01, 0x02}); // truncated message
      Object result = decoder.decode(null, null, buf);
      assertNull(result); // decoder should handle gracefully
  }
  ```
- Incorrect example:
  ```java
  @Test
  public void testDecode() {
      // Only testing valid messages, missing empty/invalid cases
      ChannelBuffer buf = createValidMessage();
      Object result = decoder.decode(null, null, buf);
      assertNotNull(result);
  }
  ```