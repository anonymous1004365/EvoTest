---
name: protocol-decoder-crc-byte-order
description: When testing protocol decoders with multiple parsing paths (standard
  and alternative), ensure byte order and buffer offset are correctly handled in the
  alternative path, especially when reading CRC/length checks. Triggering test should
  send messages that exercise the alternative decoding branch.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-crc-byte-order

## Instructions

# Protocol Decoder Alternative Path: CRC Byte Order Validation

## Instructions

- WHEN the TG encounters a protocol decoder class that implements multiple parsing paths (e.g., one for standard message format and an alternative path for a different framing format)
- THEN the TG should send a test message that exercises the **alternative parsing path**, with specific attention to:
  - **Byte order**: If the alternative path reads multi-byte values (e.g., CRC, length) using `buf.getUnsignedShort()`, verify that the byte order is explicitly set to `BIG_ENDIAN` via `buf.order(ByteOrder.BIG_ENDIAN)` before reading. If the byte order is not set, the read will use the channel's native `LITTLE_ENDIAN` byte order, causing the CRC/length check to compare incorrect bytes.
  - **Buffer reallocation**: If the alternative path calls `buf.capacity()` or `addLast()` to reallocate the buffer, ensure the content is properly retained (using `copy()` or `retain()`) before the reallocation.
  - **Return value**: Ensure the decoder returns the correct decoded object type (e.g., `String`, not `ChannelBuffer`).

- The triggering test should verify that:
  - A hex-encoded message conforming to the alternative format is correctly decoded.
  - The decoded object is of the expected type (e.g., `String`).
  - The decoded content matches the expected value (e.g., the IMEI or device ID extracted from the message).

- Common pitfalls to avoid:
  - Testing only the standard message path and assuming the alternative path works identically.
  - Forgetting that `buf.getUnsignedShort()` defaults to the **current byte order** of the buffer, which may be `LITTLE_ENDIAN` from the channel. If the protocol spec uses `BIG_ENDIAN` for the CRC check, the alternative path must call `buf.order(ByteOrder.BIG_ENDIAN)` before reading.
  - Assuming buffer content survives `capacity()` or `addLast()` operations — use `copy()` to preserve content.

- Example test (correct):
  ```java
  @Test
  public void testDecodeAlternativePath() {
      MtxProtocolDecoder decoder = new MtxProtocolDecoder();
      ByteBuf buf = Unpooled.copiedBuffer(
          Hex.decode("2424323830363933303035353930303532392c33312c302c302c302c302c302c302c302c302c302c302c302c302c302c37312c302c302a34300d0a"),
          ByteOrder.LITTLE_ENDIAN  // as received from channel
      );
      Object result = decoder.decode(null, null, buf);
      assertNotNull(result);
      assertTrue(result instanceof String);
      // Expected decoded value from the alternative path
      assertEquals("2806930055900529", result);
  }
  ```

- Example test that would miss the bug (incorrect):
  ```java
  // Only tests the standard path
  @Test
  public void testDecode() {
      MtxProtocolDecoder decoder = new MtxProtocolDecoder();
      // Only tests standard format, skipping the alternative path entirely
  }
  ```