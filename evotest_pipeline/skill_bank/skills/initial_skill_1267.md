---
name: protocol-alternative-decoding-null-handling
description: When a protocol decoder has an alternative decoding path that fails silently
  and returns an incomplete result (like null or default object), test with the specific
  input values that trigger the failure path and verify the decoded output is complete
  and correct.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- EXCEPTION_HANDLING
- VALIDATION
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: STATE_TEST
---

# protocol-alternative-decoding-null-handling

## Instructions

# Protocol Alternative Decoding Null Handling

## Instructions

- **WHEN** the TG encounters a protocol decoder class (e.g., `RuptelaProtocolDecoder`) that implements an alternative decoding path (e.g., a fallback method like `decode` that delegates to a different `decodeX` method when the primary decoding fails or returns `null`)
- **THEN** the TG should write a test that:
  1. Constructs a concrete input buffer/channel containing the specific bytes that trigger the alternative decoding path (e.g., bytes that fail the primary decoder but are passed to the fallback)
  2. Calls the decoder's decode method with that input
  3. **Asserts that the returned object is NOT null AND has all required fields populated (return type-specific validation)** — a null or default-constructed return object indicates the alternative path swallowed an error
  4. If the decoder returns a domain object (e.g., a `Position`, `DeviceSession`, or `Command`), verify key fields are set correctly, not just the return type

- **Common pitfalls to avoid**:
  - Testing only the normal/happy path where no alternative decoding is exercised
  - Testing only that no exception is thrown, without verifying the returned object's completeness
  - Assuming that if a `decode` method returns a non-null object, it must have been successfully decoded
  - Not providing concrete byte-level input that matches the real protocol format

- **Example** (correct):
  ```java
  @Test
  public void testDecodeAlternativePath() throws Exception {
      RuptelaProtocolDecoder decoder = new RuptelaProtocolDecoder(null);
      Channel channel = mock(Channel.class);
      SocketAddress remoteAddress = new InetSocketAddress("localhost", 0);
      
      // Craft byte buffer that triggers the alternative decoding path
      ByteBuf buf = Unpooled.copiedBuffer(new byte[] { 0x01, 0x02, 0x00, 0x0A, ... }); // protocol-specific bytes
      
      Object result = decoder.decode(channel, remoteAddress, buf);
      
      assertNotNull("Decoded result must not be null", result);
      assertTrue("Result must be a Position", result instanceof Position);
      Position position = (Position) result;
      assertNotNull("Position must have a device ID", position.getDeviceId());
      assertTrue("Position must have valid coordinates", position.getValid());
  }
  ```

- **Incorrect example** (too weak):
  ```java
  @Test
  public void testDecode() throws Exception {
      RuptelaProtocolDecoder decoder = new RuptelaProtocolDecoder(null);
      Object result = decoder.decode(null, null, Unpooled.EMPTY_BUFFER);
      // This may return null or an incomplete Position, and we don't check
      assertNotNull(result);  // Not enough! Need to verify result completeness
  }
  ```