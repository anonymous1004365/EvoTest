---
name: protocol-decoder-alternative-branch-validation
description: When a protocol decoder has an alternative decoding branch (like GPS
  vs. non-GPS messages), test both branches with valid and boundary data to ensure
  the decoder doesn't silently fall through without producing a result or throwing
  an error.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-alternative-branch-validation

## Instructions

# Protocol Decoder Alternative Branch Validation

## Instructions

- **WHEN** the TG encounters a protocol decoder class (e.g., extending `BaseProtocolDecoder`, `GpsGateProtocolDecoder`, etc.) that handles different message types via an `if`/`else if`/`else` chain, a switch statement, or a type-discriminating field:
  - **THEN** the TG should write parametric tests that exercise **each distinct branch** of the message handling logic.
  - **THEN** for each branch, the test MUST verify that either:
    1. The decoder returns a **non-null position object** containing valid data (e.g., latitude, longitude, time), OR
    2. The decoder returns `null` **explicitly** (not just falls through), OR
    3. The decoder throws a meaningful exception (e.g., `RuntimeException`, `IndexOutOfBoundsException`) on malformed input for that branch.

- **WHEN** the decoder parses a message with fields like device identifier, time, latitude, longitude, speed, course, etc.:
  - **THEN** the TG should test with boundary values for numeric fields (e.g., latitude `0.0`, `-90.0`, `90.0`; longitude `0.0`, `-180.0`, `180.0`; speed `0`, negative; course `0`, `360`, negative).
  - **THEN** the TG should test with missing/empty fields in the message (e.g., empty strings, insufficient tokens).
  - **THEN** the TG should verify that `position.setValid(true)` is called only when valid coordinates are present, and `position.setValid(false)` (or left as default) for missing/invalid coordinates.

- **WHEN** the decoder performs index-based access on String arrays from `String.split()` or tokenized messages:
  - **THEN** the TG should test with messages that have fewer tokens than expected, which would cause `ArrayIndexOutOfBoundsException` on the buggy version.
  - **THEN** the TG should verify the decoder handles incomplete messages gracefully (returns null or sets only available fields).

- **Common pitfalls to avoid:**
  - ❌ Testing only the "happy path" / primary branch (e.g., only GPS messages when the decoder also handles non-GPS messages)
  - ❌ Assuming the decoder returns a valid position for all message types — it may silently fall through and return the default empty position object
  - ❌ Not testing messages with fewer fields than expected — this is a common source of `ArrayIndexOutOfBoundsException` in protocol decoders
  - ❌ Forgetting to verify the `Position` object's fields (lat, lon, time) have been properly populated after decoding

- **Example (correct):**
  ```java
  @Test
  public void testDecode() throws Exception {
      // Test GPS message branch
      Position position = decoder.decode(null, null, "123456789012345,1,20250101,120000,48.8566,2.3522,100,180,10");
      assertNotNull(position);
      assertEquals(48.8566, position.getLatitude(), 0.0001);
      assertEquals(2.3522, position.getLongitude(), 0.0001);
      
      // Test non-GPS / status message branch (if applicable)
      Position statusPosition = decoder.decode(null, null, "123456789012345,0,20250101,120000,,,,,");
      // Either null or valid=false depending on design
      assertNotNull(statusPosition);
      assertFalse(statusPosition.getValid());
      
      // Test incomplete message (fewer tokens than expected)
      assertThrows(ArrayIndexOutOfBoundsException.class, () -> {
          decoder.decode(null, null, "123456789012345,1,20250101");
      });
  }
  ```

- **Example (incorrect — only testing the happy path):**
  ```java
  @Test
  public void testDecode() throws Exception {
      // Only tests the GPS branch with complete data — misses:
      // 1. Non-GPS / status message branch
      // 2. Incomplete messages with missing fields
      // 3. Edge cases for numeric fields (negative, zero, out of range)
      Position position = decoder.decode(null, null, "123456789012345,1,20250101,120000,48.8566,2.3522,100,180,10");
      assertNotNull(position);
      assertEquals(48.8566, position.getLatitude(), 0.0001);
  }
  ```