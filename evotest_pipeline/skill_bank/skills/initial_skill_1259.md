---
name: protocol-message-type-validation
description: When decoding binary protocol messages where the message type field (e.g.,
  a flag byte) determines how the payload is parsed, test that the decoder correctly
  handles all valid message type values and rejects/throws on invalid type values,
  especially when type conversion (e.g., byte to boolean) is involved.
code_tags:
- VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# protocol-message-type-validation

## Instructions

# Protocol Message Type Validation

## Instructions

WHEN the TG encounters code that decodes binary protocol messages and uses a specific byte or field value to determine message type (e.g., a flag byte for alarm/text/photo/command messages), AND that type value is validated using a type conversion (such as treating a byte as a boolean via `value != 0`):

- THEN the TG should write parametric tests that:
  1. Create a binary message with each valid message type value and verify it decodes correctly
  2. Create a binary message with an invalid/unknown message type value and verify the decoder either throws an exception (e.g., `IllegalArgumentException`, `RuntimeException`) or returns a sensible default
  3. Test boundary values of the type field (e.g., 0, 1, max valid, max byte values)

- Common pitfalls to avoid:
  - Testing only one message type (e.g., only text messages) when multiple types exist
  - Assuming the type field is boolean when it may have more than 2 valid values
  - Forgetting to test invalid/unknown type values that could cause unexpected decoder behavior
  - Using a single hardcoded byte array; instead, use a helper method to build test messages with different type values

- Concrete example (protocol decoder test):
  ```java
  // CORRECT: Test all valid message types + invalid type
  @ParameterizedTest
  @CsvSource({
      "0,  // alarm message type
      1,  // text message type
      2,  // photo message type
      255 // invalid type - should throw
  })
  void testDecodeMessageType(int typeValue) {
      byte[] msg = buildMessage((byte) typeValue, ...);
      if (typeValue >= 0 && typeValue <= 2) {
          assertDoesNotThrow(() -> decoder.decode(channel, remoteAddress, msg));
      } else {
          assertThrows(RuntimeException.class, () -> decoder.decode(channel, remoteAddress, msg));
      }
  }
  
  // INCORRECT: Testing only one message type
  @Test
  void testDecode() {
      byte[] msg = buildTextMessage();
      assertNotNull(decoder.decode(channel, remoteAddress, msg));
      // Missing: alarm type, photo type, invalid type
  }
  
  // INCORRECT: Not using a helper method, duplicating byte array construction
  @Test
  void testDecodeAlarm() {
      byte[] msg = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A};
      // ... repeated for each message type
  }
  ```

WHEN the TG encounters a protocol decoder that uses a bit flag or type byte to distinguish between messages (e.g., alarm vs text vs photo), AND the decoder validates this type using a logical condition (e.g., `type != 0` interpreted as boolean):

- THEN the TG should test that:
  1. When type == 0 (alarm/false), alarm-specific fields are parsed correctly
  2. When type == 1 (text/true), text-specific fields are parsed correctly
  3. When type > 1 (extended or invalid), the decoder handles it without crashing or leaking state

- Common pitfalls:
  - Using `assertTrue(decoded)` when the result may be different types of objects
  - Not checking that the decoded object's fields match the expected values for the given message type