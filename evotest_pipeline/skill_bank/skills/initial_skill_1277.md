---
name: alternative-protocol-decoding-test
description: When testing protocol decoders that handle multiple message formats,
  the TG should test with diverse byte sequences to ensure the decoder correctly identifies
  and processes each alternative format, catching cases where certain formats trigger
  decoding errors.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-test

## Instructions

# Testing Alternative Protocol Decoding Formats

## Instructions

- WHEN the TG encounters a protocol decoder that supports multiple message types or formats (e.g., a decoder switching on message type bytes, handling different frame structures, or using alternative parsing paths)
- THEN the TG should create parametric tests that send distinct byte sequences representing each supported message format, and verify that decoding completes without throwing an exception (e.g., `IndexOutOfBoundsException`, `IllegalArgumentException`, `NullPointerException`)
- Include at least one test case for each branch of the protocol format switch/if chain, and specifically target boundary values of format indicators (e.g., first byte, message type field, length field)
- Common pitfalls: testing only the primary/default format, testing only valid messages without exception safety, assuming all parsing paths are equally exercised by a single test input, and not verifying that the decoder does NOT crash on alternative formats
- For each test case, use `assertNotNull` on the resulting decoded object and catch any unexpected exceptions with `fail()`

### Correct Example

```java
@Test
public void testDecodeWithAlternativeFormats() throws Exception {
    // Test with primary format
    ByteBuf buf1 = Unpooled.copiedBuffer(new byte[]{0x01, 0x02, 0x03, 0x04});
    assertNotNull(decoder.decode(null, null, buf1));
    
    // Test with alternative format (different message type indicator)
    ByteBuf buf2 = Unpooled.copiedBuffer(new byte[]{0x02, 0x05, 0x06, 0x07, 0x08});
    assertNotNull(decoder.decode(null, null, buf2)); // catches IndexOutOfBoundsException bug
    
    // Test with short/long payload variants
    ByteBuf buf3 = Unpooled.copiedBuffer(new byte[]{0x03});
    assertNotNull(decoder.decode(null, null, buf3));
}
```

### Incorrect Example (Misses the Bug)

```java
@Test
public void testDecode() throws Exception {
    // Only testing primary format
    ByteBuf buf = Unpooled.copiedBuffer(new byte[]{0x01, 0x02, 0x03, 0x04});
    assertNotNull(decoder.decode(null, null, buf)); // never reaches the buggy path
}
```