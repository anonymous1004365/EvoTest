---
name: protocol-decoder-timestamp-validation
description: WHEN testing protocol decoders that parse timestamp fields from device messages, THEN use both valid timestamps and edge-case values (e.g., empty, zero, negative, or out-of-range timestamps) to ensure the decoder handles malformed data without throwing unexpected exceptions or returning corrupted position objects.
code_tags: ['NULL_CHECK', 'ARGUMENT_VALIDATION', 'CONDITIONAL_BRANCH']
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-timestamp-validation

## Instructions

# Protocol Decoder Timestamp Validation

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., `MeitrackProtocolDecoder`, `AquilaProtocolDecoder`) that extends `BaseProtocolDecoder` and parses timestamp fields from raw device messages (e.g., reading `Date` from channel buffer using methods like `readDate`, `readTime`, or custom timestamp parsing logic)
- THEN it should write parametric tests that:
  1. Send messages with **valid timestamps** (e.g., a normal date string like `"110915120000"` representing `2015-09-11 12:00:00`) to verify the decoder produces the correct `Position` object with a non-null `getFixTime()`.
  2. Send messages with **unexpected or malformed timestamp data**, such as:
     - **Empty timestamp field** (e.g., `"110915"` where a longer timestamp is expected)
     - **Zero or default timestamp value** (e.g., `"000000000000"`)
     - **Negative sign or non-numeric characters** in the timestamp portion
     - **Out-of-range values** (e.g., month=13, day=32, hour=25)
  3. Verify that for malformed timestamps, the decoder **does not throw an unexpected exception** (e.g., `StringIndexOutOfBoundsException`, `NumberFormatException`, `IllegalArgumentException`) and instead gracefully handles the data by either:
     - Skipping the malformed message (returning `null`),
     - Returning a position with a `null` or default fix time, **OR**
     - Properly rejecting the message at the protocol level.
  4. If the decoder uses `ChannelBuffer.readDate(...)` or similar date-reading utility methods, test the **boundary conditions** of those methods (e.g., very old dates, future dates, dates with different calendar eras).

- Common pitfalls to avoid:
  - **Testing only "happy path" messages** with well-formed timestamps. Protocol decoders often crash on malformed timestamps because they assume specific string lengths or numeric formats.
  - **Assuming catch-all exception handling**. Check whether the decoder has `catch (Exception e)` blocks that swallow exceptions but leave `Position` objects in an inconsistent state (e.g., `position.getFixTime()` returning `null` when it should not, or a position with corrupted other fields).
  - **Not testing the full timestamp string**. Some decoders only validate parts of a timestamp (e.g., only checking hours/minutes/seconds) but fail on missing date components.
  - **Relying solely on integration tests**. Unit-level parametric tests using raw byte buffers with manipulated timestamp fields are more targeted and reproducible.

- ✅ Correct example (Java pseudocode):
  ```java
  @ParameterizedTest
  @CsvSource({
      "010101120000,   true,  2025-01-01T12:00:00Z",   // valid
      "010101000000,   true,  2025-01-01T00:00:00Z",   // valid midnight
      ",               false, null",                     // empty
      "000000000000,   false, null",                    // all zeros
      "010101999999,   false, null",                    // invalid time
  })
  void testDecodeTimestamp(String timestamp, boolean expectValid, String expectedTime) {
      ByteBuf buf = Unpooled.buffer();
      buf.writeBytes(("$" + timestamp + ",...").getBytes(StandardCharsets.US_ASCII));
      Position position = decoder.decode(null, null, buf);
      if (expectValid) {
          assertNotNull(position);
          assertEquals(Instant.parse(expectedTime), position.getFixTime().toInstant());
      } else {
          assertNull(position);
      }
  }
  ```

- ❌ Incorrect approach (testing only happy path):
  ```java
  @Test
  void testDecode_withValidTimestamp_returnsPosition() {
      ByteBuf buf = Unpooled.buffer();
      buf.writeBytes("$010101120000,...".getBytes(StandardCharsets.US_ASCII));
      Position position = decoder.decode(null, null, buf);
      assertNotNull(position);
      assertEquals(LocalDateTime.of(2025, 1, 1, 12, 0), position.getFixTime());
  }
  // Missing tests for malformed/empty/zero timestamps that would catch the bug.
  ```