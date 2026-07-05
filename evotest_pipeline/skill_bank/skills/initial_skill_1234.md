---
name: alternative-protocol-decoding-path
description: When a protocol decoder supports multiple message formats/types and uses alternative or fallback decoding paths, tests must ensure each alternative path correctly handles valid input and properly throws exceptions for malformed input. Catches bugs where one decoding branch succeeds while another fails silently or produces wrong output.
code_tags: ['ARGUMENT_VALIDATION', 'NULL_CHECK', 'STATE_MUTATION', 'ALTERNATIVE_PROTOCOL_DECODING']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding Paths

## Instructions

- WHEN the TG encounters a protocol decoder class that implements `decode` (or similar) methods handling multiple message formats, types, or protocol versions — especially where one decoding path is tried before another as a fallback
- THEN the TG must write parameterized tests that:
  1. Test each distinct message type/format that the decoder supports, providing valid input for each
  2. Test with malformed or incomplete input for each format to verify that an exception (typically `IllegalArgumentException` or a decoder-specific exception) is thrown or the message is properly rejected
  3. Verify that the decoding result contains the expected field values (e.g., position data, device ID, timestamps) — not just that no exception is thrown
  4. For decoders in packages like `org.traccar.protocol`, use the protocol-specific test base class and helper methods (e.g., `assertNotNull(msg)`, check `msg.getDeviceId()`)

- Common pitfalls to avoid:
  - Testing only one "happy path" and assuming other decoding branches work identically
  - Testing only that no exception is thrown without verifying the decoded object contents
  - Testing with input that exercises the same code path repeatedly (e.g., same message type)
  - Forgetting to test edge cases like empty input, missing fields, or truncated messages

- **Correct example** (parameterized test with multiple message types):
  ```java
  @ParameterizedTest
  @CsvSource({
      "typeA, validPayloadForA, expectedFieldValue1",
      "typeB, validPayloadForB, expectedFieldValue2"
  })
  void testDecodeMultipleTypes(String type, String payload, String expected) {
      var decoder = new MyProtocolDecoder();
      var msg = decoder.decode(null, null, payload);
      assertNotNull(msg);
      assertEquals(expected, msg.getSomeField());
  }
  ```

- **Correct example** (testing invalid input throws exception):
  ```java
  @Test
  void testDecodeMalformedInputThrowsException() {
      var decoder = new MyProtocolDecoder();
      assertThrows(IllegalArgumentException.class, () -> {
          decoder.decode(null, null, "garbage_input");
      });
  }
  ```

- **Incorrect example** (only tests one path, no content verification):
  ```java
  @Test
  void testDecode() {
      var decoder = new MyProtocolDecoder();
      // Only tests one message type, doesn't check the result content
      assertDoesNotThrow(() -> {
          decoder.decode(null, null, "someInput");
      });
  }
  ```